from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.containers import AppContainer
from app.core.db import managed_db_session
from app.core.types import AnyIPAddress
from app.dependencies.db_session import get_db_session
from app.dependencies.host import get_host
from app.schemas.auth import AuthRequestSchema, AuthResponseSchema
from app.services.auth import AuthService
from app.utils.cookies import set_auth_cookies

router = APIRouter(prefix='/sign-in')


@router.post('/', name='auth:sign-in')
@managed_db_session
async def sign_in(
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthService, Depends(AppContainer.auth_service)],
    user_agent: Annotated[str, Header()],
    ip_address: Annotated[AnyIPAddress, Depends(get_host)],
    data: AuthRequestSchema,
) -> AuthResponseSchema:
    auth_response = await service.sign_in(db_session, data, ip_address, user_agent)
    set_auth_cookies(response, auth_response.tokens.access, auth_response.tokens.refresh)
    return auth_response
