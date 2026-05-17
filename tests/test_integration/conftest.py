import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast
from unittest.mock import patch

import pytest
from sqlalchemy import Table
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.containers import AppContainer
from tests.test_integration.mocks.model import MockModel
from tests.test_integration.mocks.repo import MockRepo
from tests.test_integration.mocks.schema import MockModelResponseSchema
from tests.test_integration.mocks.service import MockService


@pytest.fixture(scope='session')
async def db_engine() -> AsyncIterator[AsyncEngine]:
    yield await AppContainer.db_engine()


@pytest.fixture(scope='session', autouse=True)
async def setup_db(db_engine: AsyncEngine) -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(cast(Table, MockModel.__table__).create, checkfirst=True)


@pytest.fixture(scope='function')
def mock_repo() -> MockRepo:
    return MockRepo(MockModel)


@pytest.fixture(scope='function')
def mock_service(mock_repo: MockRepo) -> MockService:
    service = MockService(mock_repo)
    service.response_schema = MockModelResponseSchema
    return service


@asynccontextmanager
async def _mock_di() -> AsyncIterator[None]:
    await asyncio.sleep(0)
    yield


@asynccontextmanager
async def _mock_db(db_session: AsyncSession) -> AsyncIterator[AsyncSession]:
    await asyncio.sleep(0)
    yield db_session


@pytest.fixture
def patch_bg_job() -> Any:
    @asynccontextmanager
    async def _patch(job_module_path: str, db_session: AsyncSession) -> AsyncIterator[None]:
        await asyncio.sleep(0)
        with (
            patch(f'{job_module_path}.init_di_context', _mock_di),
            patch(f'{job_module_path}.get_db_session', lambda: _mock_db(db_session)),
        ):
            yield

    return _patch
