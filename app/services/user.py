from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repos.user import UserRepo
from app.schemas.base import Filter
from app.schemas.user import UserResponseSchema
from app.services.base import SoftDeletableService


class UserService(SoftDeletableService[UUID, User, UserResponseSchema]):
    response_schema = UserResponseSchema
    repo: UserRepo

    async def get_by_email(self, db_session: AsyncSession, email: EmailStr) -> User:
        return await self.retrieve_one_raw_by(
            db_session,
            (Filter(field='email', value=str(email)),),
        )
