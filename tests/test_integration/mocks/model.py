from sqlalchemy.orm import Mapped

from app.models.base import BaseModel
from tests.factories.base import SQLAlchemyBaseModelFactory


class MockModel(BaseModel):
    name: Mapped[str]


class MockModelFactory(SQLAlchemyBaseModelFactory[MockModel]): ...
