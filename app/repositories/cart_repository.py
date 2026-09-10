from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem


class CartRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(
        self,
        user_id: int,
    ) -> Cart | None:

        statement = select(Cart).where(
            Cart.user_id == user_id
        )

        return self.db.scalar(statement)

    def get_or_create(
        self,
        user_id: int,
    ) -> Cart:

        cart = self.get_by_user_id(user_id)

        if cart is not None:
            return cart

        cart = Cart(user_id=user_id)

        self.db.add(cart)
        self.db.flush()

        return cart

    def get_item(
        self,
        cart_id: int,
        menu_item_id: int,
    ) -> CartItem | None:

        statement = select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.menu_item_id == menu_item_id,
        )

        return self.db.scalar(statement)

    def get_items(
        self,
        cart_id: int,
    ) -> list[CartItem]:

        statement = (
            select(CartItem)
            .where(CartItem.cart_id == cart_id)
            .order_by(CartItem.id)
        )

        return list(self.db.scalars(statement).all())

    def add_item(
        self,
        cart_id: int,
        menu_item_id: int,
        quantity: int,
    ) -> CartItem:

        item = CartItem(
            cart_id=cart_id,
            menu_item_id=menu_item_id,
            quantity=quantity,
        )

        self.db.add(item)
        self.db.flush()

        return item

    def update_quantity(
        self,
        item: CartItem,
        quantity: int,
    ) -> CartItem:

        item.quantity = quantity

        self.db.flush()

        return item

    def remove_item(
        self,
        item: CartItem,
    ) -> None:

        self.db.delete(item)
        self.db.flush()
        
    def clear_cart(self, cart_id: int) -> None:
        items = self.get_items(cart_id)

        for item in items:
            self.db.delete(item)

        self.db.flush()