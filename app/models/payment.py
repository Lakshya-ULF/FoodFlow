from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    provider_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    order = relationship("Order")