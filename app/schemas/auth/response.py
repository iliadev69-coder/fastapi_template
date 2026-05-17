from app.schemas.base import BaseResponseSchema, BaseTokenSchema
from app.schemas.fields.dt_without_tz import dt_without_tz
from app.schemas.user import UserResponseSchema


class Token(BaseTokenSchema):
    nbf: dt_without_tz


class AuthToken(BaseResponseSchema):
    token: str
    expires_at: dt_without_tz


class AuthResponseTokens(BaseResponseSchema):
    access: AuthToken
    refresh: AuthToken


class AuthResponseSchema(BaseResponseSchema):
    user: UserResponseSchema
    tokens: AuthResponseTokens
