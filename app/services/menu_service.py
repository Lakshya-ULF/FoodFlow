from decimal import Decimal
from sqlalchemy.orm import Session

from app.repositories.menu_repository import MenuRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.search.menu_search import index_menu_item

class MenuService:

    def __init__(self, db: Session):
        self.db = db
        self.menu_repository = MenuRepository(db)
        self.restaurant_repository = RestaurantRepository(db)

    def get_menu(
        self,
        restaurant_id: int,
    ):
        restaurant = self.restaurant_repository.get_by_id(
            restaurant_id
        )

        if restaurant is None:
            raise ValueError("Restaurant not found")

        return self.menu_repository.get_by_restaurant(
            restaurant_id
        )

    def get_available_menu(
        self,
        restaurant_id: int,
    ):
        restaurant = self.restaurant_repository.get_by_id(
            restaurant_id
        )

        if restaurant is None:
            raise ValueError("Restaurant not found")

        return self.menu_repository.get_available_by_restaurant(
            restaurant_id
        )

    def create_item(
        self,
        restaurant_id: int,
        owner_id: int,
        name: str,
        description: str | None,
        price: Decimal,
    ):
        restaurant = self.restaurant_repository.get_by_id(
            restaurant_id
        )

        if restaurant is None:
            raise ValueError("Restaurant not found")

        if restaurant.owner_id != owner_id:
            raise PermissionError(
                "You do not own this restaurant"
            )

        if price <= 0:
            raise ValueError(
                "Price must be greater than zero"
            )

        item = self.menu_repository.create(
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            price=price,
        )

        self.db.commit()
        self.db.refresh(item)
        index_menu_item(item, restaurant)
        return item

    def update_item(
        self,
        item_id: int,
        owner_id: int,
        name: str,
        description: str | None,
        price: Decimal,
    ):
        item = self.menu_repository.get_by_id(item_id)

        if item is None:
            raise ValueError("Menu item not found")

        restaurant = self.restaurant_repository.get_by_id(
            item.restaurant_id
        )

        if restaurant is None:
            raise ValueError("Restaurant not found")

        if restaurant.owner_id != owner_id:
            raise PermissionError(
                "You do not own this restaurant"
            )

        if price <= 0:
            raise ValueError(
                "Price must be greater than zero"
            )

        item = self.menu_repository.update(
            item=item,
            name=name,
            description=description,
            price=price,
        )

        self.db.commit()
        self.db.refresh(item)
        index_menu_item(item, restaurant)
        return item

    def set_item_available(
        self,
        item_id: int,
        owner_id: int,
        is_available: bool,
    ):
        item = self.menu_repository.get_by_id(item_id)

        if item is None:
            raise ValueError("Menu item not found")

        restaurant = self.restaurant_repository.get_by_id(
            item.restaurant_id
        )

        if restaurant is None:
            raise ValueError("Restaurant not found")

        if restaurant.owner_id != owner_id:
            raise PermissionError(
                "You do not own this restaurant"
            )

        item = self.menu_repository.set_available(
            item=item,
            is_available=is_available,
        )

        self.db.commit()
        self.db.refresh(item)
        index_menu_item(item, restaurant)
        return item