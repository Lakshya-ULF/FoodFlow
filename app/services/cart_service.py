from sqlalchemy.orm import Session

from app.repositories.cart_repository import CartRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.menu_repository import MenuRepository


class CartService:

    def __init__(self, db: Session):
        self.db = db
        self.cart_repository = CartRepository(db)
        self.menu_repository = MenuRepository(db)
        self.restaurant_repository = RestaurantRepository(db)

    def get_cart(self, user_id: int):
        cart = self.cart_repository.get_by_user_id(user_id)

        if cart is None:
            return {
                "id": None,
                "user_id": user_id,
                "items": [],
            }

        items = self.cart_repository.get_items(cart.id)

        return {
            "id": cart.id,
            "user_id": cart.user_id,
            "items": [
                {
                    "id": item.id,
                    "menu_item_id": item.menu_item_id,
                    "name": item.menu_item.name,
                    "price": item.menu_item.price,
                    "quantity": item.quantity,
                }
                for item in items
            ],
    }

    def add_item(
        self,
        user_id: int,
        menu_item_id: int,
        quantity: int,
    ):
        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        # 1. Verify menu item exists
        menu_item = self.menu_repository.get_by_id(
            menu_item_id
        )

        if menu_item is None:
            raise ValueError("Menu item not found")

        # 2. Verify item is available
        if not menu_item.is_available:
            raise ValueError(
                "Menu item is not available"
            )

        # 3. Verify restaurant exists and is active
        restaurant = self.restaurant_repository.get_by_id(
            menu_item.restaurant_id
        )

        if restaurant is None:
            raise ValueError("Restaurant not found")

        if not restaurant.is_active:
            raise ValueError(
                "Restaurant is not active"
            )

        # 4. Get/create customer's cart
        cart = self.cart_repository.get_or_create(
            user_id
        )

        # 5. Enforce single-restaurant cart
        existing_items = self.cart_repository.get_items(
            cart.id
        )

        if existing_items:
            existing_restaurant_id = (
                existing_items[0].menu_item.restaurant_id
            )

            if existing_restaurant_id != menu_item.restaurant_id:
                raise ValueError(
                    "Cart can contain items from only one restaurant"
                )

        # 6. Check whether item already exists
        existing_item = self.cart_repository.get_item(
            cart.id,
            menu_item_id,
        )

        if existing_item:
            existing_item = self.cart_repository.update_quantity(
                existing_item,
                existing_item.quantity + quantity,
            )
        else:
            existing_item = self.cart_repository.add_item(
                cart_id=cart.id,
                menu_item_id=menu_item_id,
                quantity=quantity,
            )

        self.db.commit()
        self.db.refresh(existing_item)

        return existing_item

    def update_quantity(
        self,
        user_id: int,
        menu_item_id: int,
        quantity: int,
    ):
        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        cart = self.cart_repository.get_by_user_id(
            user_id
        )

        if cart is None:
            raise ValueError("Cart not found")

        item = self.cart_repository.get_item(
            cart.id,
            menu_item_id,
        )

        if item is None:
            raise ValueError(
                "Item not found in cart"
            )

        item = self.cart_repository.update_quantity(
            item,
            quantity,
        )

        self.db.commit()
        self.db.refresh(item)

        return item

    def remove_item(
        self,
        user_id: int,
        menu_item_id: int,
    ):
        cart = self.cart_repository.get_by_user_id(
            user_id
        )

        if cart is None:
            raise ValueError("Cart not found")

        item = self.cart_repository.get_item(
            cart.id,
            menu_item_id,
        )

        if item is None:
            raise ValueError(
                "Item not found in cart"
            )

        self.cart_repository.remove_item(item)

        self.db.commit()

    def clear_cart(
        self,
        user_id: int,
    ):
        cart = self.cart_repository.get_by_user_id(
            user_id
        )

        if cart is None:
            return

        items = self.cart_repository.get_items(
            cart.id
        )

        for item in items:
            self.cart_repository.remove_item(item)

        self.db.commit()