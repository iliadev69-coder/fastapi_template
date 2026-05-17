from sqlalchemy import Column, Index
from sqlalchemy.orm import Mapped

from app.models import BaseModel


class User(BaseModel):
    email: Mapped[str]
    password_hash: Mapped[str | None]
    password_salt: Mapped[str | None]

    __table_args__ = (
        Index(
            'user_email_uq_partial_idx',
            'email',
            unique=True,
            postgresql_where=Column('deleted_at').is_(None),
        ),
    )
