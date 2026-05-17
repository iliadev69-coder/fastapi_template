from hmac import compare_digest
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.config import EnvSecrets
from app.core.containers import AppContainer
from app.resources import strings

basic_auth = HTTPBasic()


def get_current_username(
    env: Annotated[EnvSecrets, Depends(AppContainer.env)],
    credentials: Annotated[HTTPBasicCredentials, Depends(basic_auth)],
) -> str:
    correct_username = compare_digest(credentials.username, env.AUTH_USERNAME)
    correct_password = compare_digest(credentials.password, env.AUTH_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=strings.INCORRECT_USERNAME_OR_PASSWORD,
            headers={'WWW-Authenticate': 'Basic'},
        )
    return credentials.username
