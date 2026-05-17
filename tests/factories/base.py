from typing import Any

from faker import Faker
from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from pydantic import BaseModel as PydanticBaseModel

from app.models.base import BaseModel as SQLAlchemyBaseModel
from app.schemas.base import BaseRequestSchema, BaseResponseSchema

_f = Faker()


class SQLAlchemyBaseModelFactory[T: SQLAlchemyBaseModel](SQLAlchemyFactory[T]):
    __faker__ = _f
    __is_base_factory__ = True
    __set_foreign_keys__ = False

    created_at = Ignore()
    updated_at = Ignore()
    deleted_at = Ignore()


class BaseModelFactory[T: PydanticBaseModel](ModelFactory[T]):
    __faker__ = _f
    __is_base_factory__ = True


class BaseRequestFactory[T: BaseRequestSchema](BaseModelFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def build_json(cls, **kwargs: Any) -> dict[str, Any]:
        return cls.build(**kwargs).model_dump(mode='json')


class BaseResponseFactory[T: BaseResponseSchema](BaseModelFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def build_json(cls, **kwargs: Any) -> dict[str, Any]:
        return cls.build(**kwargs).model_dump(mode='json')
