from uuid import UUID

from app.models import User
from app.repos.base import SoftDeletableRepo


class UserRepo(SoftDeletableRepo[UUID, User]): ...
