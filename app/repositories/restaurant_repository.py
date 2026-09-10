from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant


class RestaurantRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        restaurant_id: int,
    ) -> Restaurant | None:

        statement = select(Restaurant).where(
            Restaurant.id == restaurant_id
        )

        return self.db.scalar(statement)

    def get_all_active(
        self,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Restaurant]:

        statement = (
            select(Restaurant)
            .where(Restaurant.is_active.is_(True))
            .order_by(Restaurant.id)
            .offset(offset)
        )

        if limit is not None:
            statement = statement.limit(limit)

        return list(self.db.scalars(statement).all())

    def get_by_owner(
        self,
        owner_id: int,
    ) -> list[Restaurant]:

        statement = (
            select(Restaurant)
            .where(Restaurant.owner_id == owner_id)
            .order_by(Restaurant.id)
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        name: str,
        address: str,
        owner_id: int,
    ) -> Restaurant:

        restaurant = Restaurant(
            name=name,
            address=address,
            owner_id=owner_id,
        )

        self.db.add(restaurant)
        self.db.flush()

        return restaurant

    def update(
        self,
        restaurant: Restaurant,
        name: str,
        address: str,
    ) -> Restaurant:

        restaurant.name = name
        restaurant.address = address

        self.db.flush()

        return restaurant

    def set_active(
        self,
        restaurant: Restaurant,
        is_active: bool,
    ) -> Restaurant:

        restaurant.is_active = is_active

        self.db.flush()

        return restaurant