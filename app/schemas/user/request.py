from pydantic import EmailStr

from app.schemas.base import BaseRequestSchema


class CreateUserRequestSchema(BaseRequestSchema):
    email: EmailStr
    password_hash: str | None = None
    password_salt: str | None = None


class UpdateUserRequestSchema(BaseRequestSchema):
    email: EmailStr | None = None
    password_hash: str | None = None
    password_salt: str | None = None
