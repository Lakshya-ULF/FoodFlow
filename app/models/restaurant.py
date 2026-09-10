from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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

    owner = relationship(
        "User",
        back_populates="restaurants",
    )
    
    menu_items = relationship(
        "MenuItem",
        back_populates="restaurant",
    )