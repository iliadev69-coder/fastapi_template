from uuid import UUID

from app.models import Session
from app.repos.base import SoftDeletableRepo


class SessionRepo(SoftDeletableRepo[UUID, Session]): ...
