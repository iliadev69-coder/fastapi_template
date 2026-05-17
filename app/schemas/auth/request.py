from typing import Annotated

from pydantic import EmailStr, Field

from app.schemas.base import BaseRequestSchema, BaseTokenParamsSchema, ClientMeta


class RefreshTokenRequestSchema(BaseRequestSchema):
    refresh_token: str | None = None


class RefreshAuthRequestSchema(RefreshTokenRequestSchema, ClientMeta): ...


class AuthRequestSchema(BaseRequestSchema):
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class TokenParamsSchema(BaseTokenParamsSchema): ...
