from uuid import UUID

from app.schemas.base import AdminMeta, BaseResponseSchema, ClientMeta
from app.schemas.fields.dt_without_tz import dt_without_tz


class SessionResponseSchema(BaseResponseSchema, AdminMeta, ClientMeta):
    id: UUID
    user_id: UUID
    expires_at: dt_without_tz
    refresh_token_hash: bytes
