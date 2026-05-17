from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import env_secrets
from app.core.containers import AppContainer
from app.core.db import managed_db_session
from app.core.types import AnyIPAddress
from app.dependencies.db_session import get_db_session
from app.dependencies.host import get_host
from app.resources.exceptions.auth import AuthenticationError
from app.resources.strings import NO_AUTH_CREDENTIALS
from app.schemas.auth import AuthResponseSchema, RefreshAuthRequestSchema
from app.schemas.auth.request import RefreshTokenRequestSchema
from app.services.auth import AuthService
from app.utils.cookies import set_auth_cookies

router = APIRouter(prefix='/refresh')


@router.post('/', name='auth:refresh')
@managed_db_session
async def refresh_auth(
    request: Request,
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthService, Depends(AppContainer.auth_service)],
    user_agent: Annotated[str | None, Header()],
    ip_address: Annotated[AnyIPAddress, Depends(get_host)],
    data: RefreshTokenRequestSchema,
) -> AuthResponseSchema:
    refresh_token = data.refresh_token or request.cookies.get(
        env_secrets.REFRESH_TOKEN_COOKIE_NAME
    )
    if not refresh_token or not refresh_token.strip():
        raise AuthenticationError(NO_AUTH_CREDENTIALS)

    auth_response = await service.refresh_auth(
        db_session,
        RefreshAuthRequestSchema(
            ip_address=ip_address,
            user_agent=user_agent,
            refresh_token=refresh_token,
        ),
    )
    set_auth_cookies(response, auth_response.tokens.access, auth_response.tokens.refresh)
    return auth_response
