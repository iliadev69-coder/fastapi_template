import hashlib
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

if TYPE_CHECKING:
    from redis.asyncio import Redis

from app.asgi import app as asgi_app
from app.core.containers import AppContainer
from app.dependencies.db_session import get_db_session
from app.models import Session, User
from tests.factories.session import SessionFactory
from tests.factories.user import UserFactory


def parse_response_datetime(s: str | None) -> datetime | None:
    if s is None:
        return None
    dt = datetime.fromisoformat(s)
    return dt.astimezone(UTC).replace(tzinfo=None) if dt.tzinfo else dt


@pytest.fixture(scope='session')
def app() -> FastAPI:
    return asgi_app


@pytest.fixture(scope='session')
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client


@pytest.fixture(scope='session')
async def db_engine() -> AsyncIterator[AsyncEngine]:
    yield await AppContainer.db_engine()


@pytest.fixture(scope='session')
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    yield await AppContainer.session_factory()


@pytest.fixture(scope='session')
async def redis() -> 'Redis[Any]':
    return await AppContainer.global_redis()


@pytest.fixture(autouse=True)
async def db_session(
    app: FastAPI,
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async_session = session_factory()
    app.dependency_overrides[get_db_session] = lambda: async_session
    yield async_session
    await async_session.rollback()
    await async_session.close()


@pytest.fixture(scope='session', autouse=True)
async def init_db(db_engine: AsyncEngine) -> None:
    async with db_engine.begin() as conn:
        stmt = text("SELECT c.relname FROM pg_class c WHERE c.relkind = 'S';")
        sequences = (await conn.execute(stmt)).scalars().all()
        for sequence in sequences:
            await conn.execute(text(f'ALTER SEQUENCE {sequence} RESTART;'))


@pytest.fixture(autouse=True)
async def clean_all_tables(db_engine: AsyncEngine) -> None:
    stmt = text("SELECT t.table_name FROM information_schema.tables t WHERE table_schema='public'")
    async with db_engine.begin() as conn:
        tables = (await conn.execute(stmt)).scalars().all()
        tables = [
            t_name
            for t_name in tables
            if not t_name.startswith('pg_') and not t_name.startswith('alembic')
        ]
        for table_name in tables:
            await conn.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE;'))


@pytest.fixture(autouse=True)
async def clean_redis(redis: 'Redis[Any]') -> None:
    await redis.flushall()


@pytest.fixture
def test_user_email() -> str:
    return 'test@example.com'


@pytest.fixture
def test_user_password() -> str:
    return 'testpassword123'


@pytest.fixture
async def test_user(
    db_session: AsyncSession,
    test_user_email: str,
    test_user_password: str,
) -> User:
    password_service = await AppContainer.password_service()
    password_hash, password_salt = password_service.generate_password_hash_and_salt(
        test_user_password
    )
    user = UserFactory.build(
        email=test_user_email,
        password_hash=password_hash,
        password_salt=password_salt,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
def test_user_id(test_user: User) -> UUID:
    return test_user.id


@pytest.fixture
def test_refresh_token() -> str:
    return 'test-refresh-token-123'


@pytest.fixture
async def test_session(
    db_session: AsyncSession,
    test_user: User,
    test_refresh_token: str,
) -> Session:
    refresh_token_hash = hashlib.sha256(test_refresh_token.encode()).digest()
    session = SessionFactory.build(
        user_id=test_user.id,
        refresh_token_hash=refresh_token_hash,
    )
    db_session.add(session)
    await db_session.commit()
    return session
