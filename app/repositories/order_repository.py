from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order
from app.models.order_item import OrderItem


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: int) -> Order | None:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )

        return self.db.scalar(statement)

    def get_by_user(self, user_id: int) -> list[Order]:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.user_id == user_id)
            .order_by(Order.id.desc())
        )

        return list(self.db.scalars(statement).all())

    def create_order(
        self,
        user_id: int,
        restaurant_id: int,
        status: str,
        payment_status: str,
        total_amount: Decimal,
    ) -> Order:
        order = Order(
            user_id=user_id,
            restaurant_id=restaurant_id,
            status=status,
            payment_status=payment_status,
            total_amount=total_amount,
        )

        self.db.add(order)
        self.db.flush()

        return order

    def create_order_item(
        self,
        order_id: int,
        menu_item_id: int,
        item_name: str,
        unit_price: Decimal,
        quantity: int,
    ) -> OrderItem:
        item = OrderItem(
            order_id=order_id,
            menu_item_id=menu_item_id,
            item_name=item_name,
            unit_price=unit_price,
            quantity=quantity,
        )

        self.db.add(item)
        self.db.flush()

        return item
    
    def get_by_restaurant(
        self,
        restaurant_id: int,
    ) -> list[Order]:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.restaurant_id == restaurant_id)
            .order_by(Order.id.desc())
        )

        return list(self.db.scalars(statement).all())