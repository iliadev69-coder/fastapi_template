from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import env_secrets
from app.core.containers import AppContainer
from app.core.db import managed_db_session
from app.dependencies.current_user import get_current_user
from app.dependencies.db_session import get_db_session
from app.resources.exceptions.auth import AuthenticationError
from app.resources.strings import NO_AUTH_CREDENTIALS
from app.schemas.auth import Token
from app.schemas.auth.request import RefreshTokenRequestSchema
from app.services.auth import AuthService
from app.utils.cookies import delete_auth_cookies

router = APIRouter(prefix='/logout')


@router.post('/', name='auth:logout', status_code=status.HTTP_204_NO_CONTENT)
@managed_db_session
async def logout(
    request: Request,
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthService, Depends(AppContainer.auth_service)],
    current_user: Annotated[Token, Depends(get_current_user)],
    data: RefreshTokenRequestSchema,
) -> None:
    refresh_token = data.refresh_token or request.cookies.get(
        env_secrets.REFRESH_TOKEN_COOKIE_NAME
    )
    if not refresh_token or not refresh_token.strip():
        raise AuthenticationError(NO_AUTH_CREDENTIALS)

    await service.logout(db_session, refresh_token, current_user.id)
    delete_auth_cookies(response)
