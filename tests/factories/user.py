from app.models.user import User
from app.schemas.user.response import UserResponseSchema
from tests.factories.base import BaseModelFactory, SQLAlchemyBaseModelFactory


class UserFactory(SQLAlchemyBaseModelFactory[User]): ...


class UserResponseFactory(BaseModelFactory[UserResponseSchema]): ...
