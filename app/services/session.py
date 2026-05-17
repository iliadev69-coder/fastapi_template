import hashlib
import secrets
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Session
from app.repos.session import SessionRepo
from app.schemas.auth import AuthToken
from app.schemas.base import Filter
from app.schemas.session import (
    CreateSessionRequestSchema,
    CreateSessionWithoutRefreshSchema,
    SessionResponseSchema,
)
from app.services.base import SoftDeletableService


class SessionService(SoftDeletableService[UUID, Session, SessionResponseSchema]):
    response_schema = SessionResponseSchema
    repo: SessionRepo

    def __init__(
        self,
        repo: SessionRepo,
        refresh_token_exp_delta: timedelta,
        refresh_token_n_bytes: int,
    ) -> None:
        super().__init__(repo)
        self._refresh_token_exp_delta = refresh_token_exp_delta
        self._refresh_token_n_bytes = refresh_token_n_bytes

    async def soft_delete_by_refresh_token(
        self,
        db_session: AsyncSession,
        refresh_token: str,
    ) -> Session:
        refresh_token_hash = self.secure_hash(refresh_token)
        session = await self.soft_delete_one_by(
            db_session,
            [Filter(field='refresh_token_hash', op='=', value=refresh_token_hash)],
        )
        return session

    async def create_with_refresh_gen(
        self,
        db_session: AsyncSession,
        when: datetime,
        data: CreateSessionWithoutRefreshSchema,
    ) -> tuple[SessionResponseSchema, AuthToken]:
        refresh, refresh_hash = self.generate_refresh_pair()
        expires_at = when + self._refresh_token_exp_delta
        refresh_token = AuthToken(
            token=refresh,
            expires_at=expires_at,
        )
        session = await self.create(
            db_session,
            CreateSessionRequestSchema(
                **data.model_dump(),
                refresh_token_hash=refresh_hash,
                expires_at=expires_at,
            ),
        )
        return session, refresh_token

    def generate_refresh_pair(self) -> tuple[str, bytes]:
        refresh = secrets.token_bytes(self._refresh_token_n_bytes).hex()
        refresh_hash = self.secure_hash(refresh)
        return refresh, refresh_hash

    @staticmethod
    def secure_hash(refresh: str) -> bytes:
        return hashlib.sha256(refresh.encode()).digest()
