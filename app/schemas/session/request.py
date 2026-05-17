from uuid import UUID

from app.schemas.base import ClientMeta
from app.schemas.fields.dt_without_tz import dt_without_tz


class CreateSessionWithoutRefreshSchema(ClientMeta):
    user_id: UUID


class CreateSessionRequestSchema(CreateSessionWithoutRefreshSchema):
    refresh_token_hash: bytes
    expires_at: dt_without_tz
