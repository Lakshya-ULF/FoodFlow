from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, Text
from app.db.base import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    payload: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )