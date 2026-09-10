from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.main_menu import MenuItem


class MenuRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        item_id: int,
    ) -> MenuItem | None:

        statement = select(MenuItem).where(
            MenuItem.id == item_id
        )

        return self.db.scalar(statement)

    def get_by_restaurant(
        self,
        restaurant_id: int,
    ) -> list[MenuItem]:

        statement = (
            select(MenuItem)
            .where(
                MenuItem.restaurant_id == restaurant_id
            )
            .order_by(MenuItem.id)
        )

        return list(self.db.scalars(statement).all())

    def get_available_by_restaurant(
        self,
        restaurant_id: int,
    ) -> list[MenuItem]:

        statement = (
            select(MenuItem)
            .where(
                MenuItem.restaurant_id == restaurant_id,
                MenuItem.is_available.is_(True),
            )
            .order_by(MenuItem.id)
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        restaurant_id: int,
        name: str,
        description: str | None,
        price: float,
    ) -> MenuItem:

        item = MenuItem(
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            price=price,
        )

        self.db.add(item)
        self.db.flush()

        return item

    def update(
        self,
        item: MenuItem,
        name: str,
        description: str | None,
        price: float,
    ) -> MenuItem:

        item.name = name
        item.description = description
        item.price = price

        self.db.flush()

        return item

    def set_available(
        self,
        item: MenuItem,
        is_available: bool,
    ) -> MenuItem:

        item.is_available = is_available

        self.db.flush()

        return item