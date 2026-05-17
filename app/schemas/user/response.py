from uuid import UUID

from app.schemas.base import AdminMeta, BaseResponseSchema


class UserResponseSchema(BaseResponseSchema, AdminMeta):
    id: UUID
    email: str
