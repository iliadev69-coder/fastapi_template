from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import BYTEA, INET
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import AnyIPAddress
from app.models import BaseModel


class Session(BaseModel):
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id', ondelete='RESTRICT'), nullable=False
    )
    ip_address: Mapped[AnyIPAddress | None] = mapped_column(INET)
    user_agent: Mapped[str | None]
    expires_at: Mapped[datetime]
    refresh_token_hash: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
