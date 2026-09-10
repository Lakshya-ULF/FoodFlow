from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DeliveryAssignment(Base):
    __tablename__ = "delivery_assignments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )

    delivery_partner_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_partners.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="assigned",
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

    delivery_partner = relationship("DeliveryPartner")

    __table_args__ = (
        UniqueConstraint(
            "order_id",
            name="uq_delivery_assignment_order",
        ),
    )