from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.types import AnyIPAddress
from app.resources.exceptions import NotFoundError, ValidationError
from app.resources.exceptions.auth import AuthorizationError
from app.resources.strings import INCORRECT_USERNAME_OR_PASSWORD, NO_AUTH_CREDENTIALS
from app.schemas.auth import (
    AuthRequestSchema,
    AuthResponseSchema,
    AuthResponseTokens,
    RefreshAuthRequestSchema,
)
from app.schemas.base import ClientMeta, Filter
from app.schemas.session import CreateSessionWithoutRefreshSchema
from app.schemas.user import UserResponseSchema
from app.services.jwt import JWTService
from app.services.password import PasswordService
from app.services.session import SessionService
from app.services.user import UserService
from app.utils.time import now_without_tz


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        password_service: PasswordService,
        jwt_service: JWTService,
        session_service: SessionService,
    ) -> None:
        self.user_service = user_service
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.session_service = session_service

    async def sign_in(
        self,
        db_session: AsyncSession,
        data: AuthRequestSchema,
        ip_address: AnyIPAddress,
        user_agent: str,
    ) -> AuthResponseSchema:
        try:
            user = await self.user_service.get_by_email(db_session, data.email)
        except NotFoundError as exc:
            raise ValidationError(INCORRECT_USERNAME_OR_PASSWORD) from exc

        await self.password_service.verify(user, data.password)

        return await self._generate_tokens(
            db_session,
            user=self.user_service.serialize(user),
            client_meta=ClientMeta(ip_address=ip_address, user_agent=user_agent),
        )

    async def _generate_tokens(
        self,
        db_session: AsyncSession,
        user: UserResponseSchema,
        client_meta: ClientMeta,
    ) -> AuthResponseSchema:
        when = now_without_tz()
        access = await self.jwt_service.generate_access_token(user_id=user.id, when=when)
        _, refresh = await self.session_service.create_with_refresh_gen(
            db_session=db_session,
            when=when,
            data=CreateSessionWithoutRefreshSchema(
                user_id=user.id,
                ip_address=client_meta.ip_address,
                user_agent=client_meta.user_agent,
            ),
        )
        return AuthResponseSchema(
            user=user,
            tokens=AuthResponseTokens(access=access, refresh=refresh),
        )

    async def refresh_auth(
        self,
        db_session: AsyncSession,
        data: RefreshAuthRequestSchema,
    ) -> AuthResponseSchema:
        if not data.refresh_token or not data.refresh_token.strip():
            raise ValidationError(NO_AUTH_CREDENTIALS)
        session = await self.session_service.soft_delete_by_refresh_token(
            db_session,
            data.refresh_token,
        )
        user = await self.user_service.retrieve(db_session, session.user_id)
        return await self._generate_tokens(
            db_session=db_session,
            user=user,
            client_meta=ClientMeta(ip_address=data.ip_address, user_agent=data.user_agent),
        )

    async def logout(
        self,
        db_session: AsyncSession,
        refresh_token: str,
        user_id: UUID,
    ) -> None:
        refresh_token_hash = self.session_service.secure_hash(refresh_token)
        session = await self.session_service.retrieve_one_raw_by(
            db_session,
            [Filter(field='refresh_token_hash', op='=', value=refresh_token_hash)],
        )
        if session.user_id != user_id:
            raise AuthorizationError
        await self.session_service.soft_delete(db_session, session.id)
