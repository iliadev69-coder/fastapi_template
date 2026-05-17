from uuid import UUID

from app.repos.base import SoftDeletableRepo
from tests.test_integration.mocks.model import MockModel


class MockRepo(SoftDeletableRepo[UUID, MockModel]): ...
