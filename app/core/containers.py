from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from logging import basicConfig
from operator import attrgetter
from sys import stdout
from typing import ClassVar, cast

from fastapi import FastAPI
from httpx import AsyncClient, Timeout
from saq import Queue
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.types import Lifespan
from that_depends import BaseContainer, container_context, providers

from app import models
from app.core.config import EnvSecrets
from app.core.db import DBSessionMiddleware
from app.core.logging import setup_logger
from app.core.redis_client import redis_client
from app.repos.session import SessionRepo
from app.repos.user import UserRepo
from app.resources.exc_handlers import exception_handlers
from app.resources.openapi import app_description, contact, openapi_tags
from app.services.auth import AuthService
from app.services.jwt import JWTService
from app.services.password import PasswordService
from app.services.session import SessionService
from app.services.user import UserService

logger = setup_logger(__name__)


async def init_di_context() -> AsyncIterator[None]:
    async with container_context(AppContainer):
        yield


@asynccontextmanager
async def lifespan(app: Callable[[FastAPI], AsyncIterator[None]]) -> AsyncIterator[None]:
    logger.info('Initiate resources at service startup')
    await AppContainer.init_resources()
    yield
    logger.info('Shut down resources at shutdown')
    await AppContainer.tear_down()


class AppContainer(BaseContainer):
    env = providers.Singleton(EnvSecrets)

    db_engine = providers.Singleton(
        create_async_engine,
        url=env.DB_DSN,
        echo=False,
        pool_size=env.PG_POOL_SIZE,
        max_overflow=env.PG_MAX_OVERFLOW,
        pool_recycle=env.PG_POOL_RECYCLE,
    )

    global_redis = providers.Resource(
        redis_client,
        url=env.REDIS_DSN,
    )

    saq_queue = providers.Factory(
        Queue.from_url,
        env.saq_redis_url,
    )

    session_factory = providers.Singleton(
        async_sessionmaker[AsyncSession],
        db_engine.cast,
        expire_on_commit=False,
        autoflush=True,
    )

    base_middlewares: ClassVar = [
        providers.Factory(
            Middleware,
            cls=DBSessionMiddleware,
            session_factory=session_factory.cast,
        ),
        providers.Factory(
            Middleware,
            cls=CORSMiddleware,
            allow_origins=env.CORS_ALLOW_ORIGINS,
            allow_credentials=env.CORS_ALLOW_CREDENTIALS,
            allow_methods=env.CORS_ALLOW_METHODS,
            allow_headers=env.CORS_ALLOW_HEADERS,
        ),
    ]

    middlewares = providers.List(*base_middlewares)

    http_timeout = providers.Singleton(Timeout, timeout=60)
    http_client = providers.Factory(AsyncClient, timeout=http_timeout.cast)

    logging = providers.Factory(
        basicConfig,
        stream=stdout,
        level=env.LOGGING_LEVEL,
        format=env.LOGGING_FORMAT,
    )

    servers = providers.List(
        providers.Dict(
            url=env.api_root_path_non_empty,
            description=env.ENV,
        ),
    )

    app_factory = providers.Factory(
        FastAPI,
        root_path=env.API_ROOT_PATH,
        title=env.APP_TITLE,
        debug=env.DEBUG,
        version=env.VERSION,
        openapi_url=env.OPENAPI_URL,
        docs_url='/docs',
        redoc_url='/redoc',
        exception_handlers=exception_handlers,
        description=app_description,
        middleware=middlewares.cast,
        servers=servers.cast,
        openapi_tags=openapi_tags,
        contact=contact,
        lifespan=cast(Lifespan[FastAPI], lifespan),
        generate_unique_id_function=attrgetter('name'),
    )

    user_repo = providers.Factory(UserRepo, model=models.User)
    session_repo = providers.Factory(SessionRepo, model=models.Session)

    password_service = providers.Factory(PasswordService)

    jwt_service = providers.Factory(
        JWTService,
        jwt_issuer=env.APP_TITLE,
        jwt_secret_key=env.JWT_SECRET_KEY,
        jwt_algorithms=env.ALGORITHMS,
        access_token_exp_delta=env.ACCESS_TOKEN_EXP_DELTA,
        jwt_not_before_gap=env.NOT_BEFORE_GAP,
    )

    session_service = providers.Factory(
        SessionService,
        repo=session_repo.cast,
        refresh_token_exp_delta=env.REFRESH_TOKEN_EXP_DELTA,
        refresh_token_n_bytes=env.REFRESH_TOKEN_N_BYTES,
    )

    user_service = providers.Factory(UserService, repo=user_repo.cast)

    auth_service = providers.Factory(
        AuthService,
        user_service=user_service.cast,
        password_service=password_service.cast,
        jwt_service=jwt_service.cast,
        session_service=session_service.cast,
    )
