from fastapi import Response

from app.core.config import env_secrets
from app.schemas.auth import AuthToken


def set_auth_cookies(
    response: Response,
    access_token: AuthToken,
    refresh_token: AuthToken,
) -> None:
    """Set access and refresh token cookies in the response."""
    # Set access token cookie
    response.set_cookie(
        key=env_secrets.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token.token,
        expires=int(access_token.expires_at.timestamp()),
        httponly=env_secrets.COOKIE_HTTPONLY,
        secure=env_secrets.COOKIE_SECURE,
        samesite=env_secrets.COOKIE_SAMESITE,
        path='/',
    )

    # Set refresh token cookie
    response.set_cookie(
        key=env_secrets.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token.token,
        expires=int(refresh_token.expires_at.timestamp()),
        httponly=env_secrets.COOKIE_HTTPONLY,
        secure=env_secrets.COOKIE_SECURE,
        samesite=env_secrets.COOKIE_SAMESITE,
        path='/',
    )


def delete_auth_cookies(response: Response) -> None:
    """Delete access and refresh token cookies from the response."""
    response.delete_cookie(
        key=env_secrets.ACCESS_TOKEN_COOKIE_NAME,
        httponly=env_secrets.COOKIE_HTTPONLY,
        secure=env_secrets.COOKIE_SECURE,
        samesite=env_secrets.COOKIE_SAMESITE,
        path='/',
    )
    response.delete_cookie(
        key=env_secrets.REFRESH_TOKEN_COOKIE_NAME,
        httponly=env_secrets.COOKIE_HTTPONLY,
        secure=env_secrets.COOKIE_SECURE,
        samesite=env_secrets.COOKIE_SAMESITE,
        path='/',
    )
