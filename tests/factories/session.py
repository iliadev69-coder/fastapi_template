from app.models.session import Session
from tests.factories.base import SQLAlchemyBaseModelFactory


class SessionFactory(SQLAlchemyBaseModelFactory[Session]): ...
