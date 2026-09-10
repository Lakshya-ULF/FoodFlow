from sqlalchemy.orm import Session
from app.core.cache import Cache
from app.search.restaurant_search import index_restaurant
from app.repositories.restaurant_repository import RestaurantRepository
from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
)

class RestaurantService:

    def __init__(self, db: Session):
        self.db = db
        self.restaurant_repository = RestaurantRepository(db)

    def get_restaurant(
        self,
        restaurant_id: int,
    ):
        restaurant = self.restaurant_repository.get_by_id(
            restaurant_id
        )

        if restaurant is None:
            raise NotFoundError("Restaurant not found")

        return restaurant

    def get_active_restaurants(self):
        cache_key = "restaurants:active"

        cached_restaurants = Cache.get(cache_key)

        if cached_restaurants is not None:
            return cached_restaurants

        restaurants = self.restaurant_repository.get_all_active()

        result = [
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "owner_id": restaurant.owner_id,
                "is_active": restaurant.is_active,
            }
            for restaurant in restaurants
        ]

        Cache.set(
            cache_key,
            result,
            ttl=60,
        )

        return result

    def get_owner_restaurants(
        self,
        owner_id: int,
    ):
        return self.restaurant_repository.get_by_owner(
            owner_id
        )

    def create_restaurant(
        self,
        name: str,
        address: str,
        owner_id: int,
    ):
        restaurant = self.restaurant_repository.create(
            name=name,
            address=address,
            owner_id=owner_id,
        )

        self.db.commit()
        self.db.refresh(restaurant)
        Cache.delete("restaurants:active")
        index_restaurant(restaurant)
        return restaurant

    def update_restaurant(
        self,
        restaurant_id: int,
        owner_id: int,
        name: str,
        address: str,
    ):
        restaurant = self.get_restaurant(restaurant_id)

        if restaurant.owner_id != owner_id:
            raise ForbiddenError(
                "You do not own this restaurant"
            )

        restaurant = self.restaurant_repository.update(
            restaurant=restaurant,
            name=name,
            address=address,
        )

        self.db.commit()
        self.db.refresh(restaurant)
        Cache.delete("restaurants:active")
        index_restaurant(restaurant)
        return restaurant

    def set_restaurant_active(
        self,
        restaurant_id: int,
        owner_id: int,
        is_active: bool,
    ):
        restaurant = self.get_restaurant(restaurant_id)

        if restaurant.owner_id != owner_id:
            raise ForbiddenError(
                "You do not own this restaurant"
            )

        restaurant = self.restaurant_repository.set_active(
            restaurant=restaurant,
            is_active=is_active,
        )

        self.db.commit()
        self.db.refresh(restaurant)
        Cache.delete("restaurants:active")
        index_restaurant(restaurant)
        return restaurant