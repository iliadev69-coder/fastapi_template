from datetime import timedelta
from secrets import token_urlsafe
from typing import Annotated, Literal

from pydantic import Field
from pydantic_settings import BaseSettings

from app.resources.regexps import semver_re

type CookieSameSite = Literal['lax', 'strict', 'none']

type LoggingLevel = Literal[
    'CRITICAL',
    'FATAL',
    'ERROR',
    'WARNING',
    'WARN',
    'INFO',
    'DEBUG',
    'NOTSET',
]


class EnvSecrets(BaseSettings):
    class Config:
        env_file = '.env'

    SERVICE_NAME: str = 'fastapi-template'
    APP_TITLE: str = 'FastAPI Template'
    DEBUG: bool = False
    ENV: str = 'dev'
    VERSION: Annotated[str, Field(pattern=semver_re)] = '0.1.0'
    API_ROOT_PATH: str = ''
    OPENAPI_URL: str = '/openapi.json'

    DB_DSN: str = 'postgresql+asyncpg://user:password@postgres/database'
    PG_POOL_SIZE: int = 10
    PG_MAX_OVERFLOW: int = 5
    PG_POOL_RECYCLE: int = 1800

    REDIS_DSN: str = 'redis://redis'

    JWT_SECRET_KEY: str = Field(default_factory=lambda: token_urlsafe(32))
    ACCESS_TOKEN_EXP_DELTA: timedelta = timedelta(minutes=10)
    REFRESH_TOKEN_EXP_DELTA: timedelta = timedelta(days=1)
    REFRESH_TOKEN_N_BYTES: int = 32
    NOT_BEFORE_GAP: timedelta = timedelta(minutes=5)
    ALGORITHMS: list[str] = ['HS256']

    AUTH_USERNAME: str = 'user'
    AUTH_PASSWORD: str = Field(default_factory=lambda: token_urlsafe(16))

    ACCESS_TOKEN_COOKIE_NAME: str = 'access_token'
    REFRESH_TOKEN_COOKIE_NAME: str = 'refresh_token'
    COOKIE_HTTPONLY: bool = True
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: CookieSameSite = 'lax'

    ENABLE_DOCS: bool = True

    CORS_ALLOW_ORIGINS: list[str] = ['*']
    CORS_ALLOW_METHODS: list[str] = ['*']
    CORS_ALLOW_HEADERS: list[str] = ['*']
    CORS_ALLOW_CREDENTIALS: bool = True

    LOGGING_LEVEL: LoggingLevel = 'INFO'
    LOGGING_FORMAT: str = '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s'

    @property
    def saq_redis_url(self) -> str:
        return f'{self.REDIS_DSN}/0'

    @property
    def openapi_url(self) -> str:
        return self.API_ROOT_PATH + self.OPENAPI_URL

    @property
    def api_root_path_non_empty(self) -> str:
        return self.API_ROOT_PATH or '/'


env_secrets = EnvSecrets()
