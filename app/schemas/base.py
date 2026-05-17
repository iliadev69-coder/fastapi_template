import re
import typing
from collections.abc import Sequence
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.ip_address import AnyIPAddress
from app.models.base import BaseModel as SQLAlchemyBaseModel
from app.resources.enums.order_by import OrderByDirections
from app.schemas.fields.dt_without_tz import dt_without_tz
from app.schemas.fields.timestamp import timestamp


class BaseResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseRequestSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CreateUpdateMeta(BaseModel):
    created_at: dt_without_tz
    updated_at: dt_without_tz


class AdminMeta(CreateUpdateMeta):
    deleted_at: dt_without_tz | None = None


class PaginationMetaSchema(BaseModel):
    limit: int
    total: int
    current_page: int
    last_page: int


class PaginatedResponseSchema[T](BaseResponseSchema):
    meta: PaginationMetaSchema
    data: Sequence[T]


class ClientMeta(BaseRequestSchema):
    ip_address: AnyIPAddress | None = None
    user_agent: str | None = None


class OrderBy(BaseModel):
    field: str
    direction: OrderByDirections = OrderByDirections.ASC
    model: type[SQLAlchemyBaseModel] | None = None


class BaseOrderBySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    def build_order_by(self, **kwargs: Any) -> list[OrderBy]:
        data = self.model_dump(exclude_unset=True, exclude_none=True)
        result = []
        for field_name, direction in data.items():
            model = kwargs.get(field_name)
            result.append(OrderBy(field=field_name, direction=direction, model=model))
        return result


FilterOp = Literal[
    'eq',
    '=',
    'ilike',
    '~=',
    'is',
    'is_not',
    'in',
    'gt',
    '>',
    'ge',
    '>=',
    'lt',
    '<',
    'le',
    '<=',
    '!=',
]
filter_op_values = typing.get_args(FilterOp)


class Filter(BaseModel):
    field: str
    op: FilterOp = '='
    value: Any | None
    model: type[SQLAlchemyBaseModel] | None = None


class OrFilterGroup(BaseModel):
    filters: list[Filter]


class BaseFiltersSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    def build_filters(
        self,
        *,
        exclude: set[str] | None = None,
        **field_models: type[SQLAlchemyBaseModel],
    ) -> list[Filter]:
        fields_data = self.model_dump(
            exclude_unset=True, exclude_none=True, exclude=exclude or set()
        )
        filters: list[Filter] = []
        for k, v in fields_data.items():
            op: FilterOp
            if suffix := re.search(r'__(\w+)$', k):
                parsed_op = suffix.group(1)
                if parsed_op not in filter_op_values:
                    raise ValueError
                field_name = k[: -len(suffix.group(0))]
                op = typing.cast(FilterOp, parsed_op)
            else:
                field_name = k
                op = '='

            model = field_models.get(field_name)
            filters.append(Filter(field=field_name, op=op, value=v, model=model))
        return filters


class BaseTokenSchema(BaseResponseSchema):
    sub: UUID
    iss: str
    nbf: timestamp
    exp: dt_without_tz
    iat: dt_without_tz

    @property
    def id(self) -> UUID:
        return self.sub


class BaseTokenParamsSchema(BaseRequestSchema): ...
