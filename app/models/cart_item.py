from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id"),
        nullable=False,
        index=True,
    )

    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        nullable=False,
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

    cart = relationship(
        "Cart",
        back_populates="items",
    )

    menu_item = relationship(
        "MenuItem",
    )

    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "menu_item_id",
            name="uq_cart_menu_item",
        ),
    )