from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core.config import env_secrets
from app.core.containers import AppContainer
from app.resources.exceptions.auth import AuthenticationError
from app.resources.strings import INVALID_TOKEN, NO_AUTH_CREDENTIALS
from app.schemas.auth import Token
from app.services.jwt import JWTService

bearer_security_scheme = HTTPBearer(auto_error=False)


def _get_token_from_request(
    request: Request,
    bearer: HTTPAuthorizationCredentials | None,
) -> str | None:
    if bearer and bearer.credentials:
        return bearer.credentials
    return request.cookies.get(env_secrets.ACCESS_TOKEN_COOKIE_NAME)


def get_current_user(
    request: Request,
    jwt_service: Annotated[JWTService, Depends(AppContainer.jwt_service)],
    bearer: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_security_scheme)],
) -> Token:
    token_string = _get_token_from_request(request, bearer)
    if not token_string:
        raise AuthenticationError(NO_AUTH_CREDENTIALS)
    try:
        return Token(**jwt_service.decode_token(token_string))
    except InvalidTokenError as e:
        raise AuthenticationError(INVALID_TOKEN) from e
    except ValidationError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e)) from e


def get_current_user_optional(
    request: Request,
    jwt_service: Annotated[JWTService, Depends(AppContainer.jwt_service)],
    bearer: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_security_scheme)],
) -> Token | None:
    token_string = _get_token_from_request(request, bearer)
    if not token_string:
        return None
    try:
        return Token(**jwt_service.decode_token(token_string))
    except (InvalidTokenError, ValidationError):
        return None
