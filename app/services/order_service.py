from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.constants import OrderStatus, PaymentStatus
from app.repositories.cart_repository import CartRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.order_state_service import OrderStateService
from app.services.order_notification_service import (
    OrderNotificationService,
)
from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    ValidationError,
)

class OrderService:
    def __init__(self, db: Session):
        self.db = db

        self.cart_repository = CartRepository(db)
        self.menu_repository = MenuRepository(db)
        self.order_repository = OrderRepository(db)
        self.restaurant_repository = RestaurantRepository(db)
        self.order_notification_service = OrderNotificationService(db)

    def checkout(self, user_id: int):
        cart = self.cart_repository.get_by_user_id(user_id)

        if cart is None:
            raise ValidationError("Cart is empty")

        cart_items = self.cart_repository.get_items(cart.id)

        if not cart_items:
            raise ValidationError("Cart is empty")

        # All items must belong to the same restaurant.
        restaurant_id = cart_items[0].menu_item.restaurant_id

        total_amount = Decimal("0")

        for cart_item in cart_items:
            menu_item = self.menu_repository.get_by_id(
                cart_item.menu_item_id
            )

            if menu_item is None:
                raise NotFoundError("Menu item no longer exists")

            if not menu_item.is_available:
                raise ValidationError(
                    f"Menu item '{menu_item.name}' is no longer available"
                )

            if menu_item.restaurant_id != restaurant_id:
                raise ValidationError(
                    "Cart contains items from multiple restaurants"
                )

            total_amount += (
                Decimal(str(menu_item.price))
                * cart_item.quantity
            )

        order = self.order_repository.create_order(
            user_id=user_id,
            restaurant_id=restaurant_id,
            status=OrderStatus.PAYMENT_PENDING,
            payment_status=PaymentStatus.PENDING,
            total_amount=total_amount,
        )

        for cart_item in cart_items:
            menu_item = self.menu_repository.get_by_id(
                cart_item.menu_item_id
            )

            self.order_repository.create_order_item(
                order_id=order.id,
                menu_item_id=menu_item.id,
                item_name=menu_item.name,
                unit_price=Decimal(str(menu_item.price)),
                quantity=cart_item.quantity,
            )

        # Cart is cleared only after the order and order items
        # have been created successfully.
        self.cart_repository.clear_cart(cart.id)
        self.db.commit()
        self.db.refresh(order)

        return self.order_repository.get_by_id(order.id)
    
    def get_order(self, order_id: int, user_id: int):
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise NotFoundError("Order not found")

        if order.user_id != user_id:
            raise ForbiddenError("You do not have access to this order")

        return order

    def get_user_orders(self, user_id: int):
        return self.order_repository.get_by_user(user_id)
    
    def get_restaurant_orders(
        self,
        restaurant_id: int,
        owner_id: int,
    ):
        restaurant = self.restaurant_repository.get_by_id(
            restaurant_id
        )

        if restaurant is None:
            raise NotFoundError("Restaurant not found")

        if restaurant.owner_id != owner_id:
            raise ForbiddenError(
                "You do not own this restaurant"
            )

        return self.order_repository.get_by_restaurant(
            restaurant_id
        )

    def accept_order(
        self,
        order_id: int,
        owner_id: int,
    ):
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise NotFoundError("Order not found")

        restaurant = self.restaurant_repository.get_by_id(
            order.restaurant_id
        )

        if restaurant is None:
            raise NotFoundError("Restaurant not found")

        if restaurant.owner_id != owner_id:
            raise ForbiddenError(
                "You do not own this restaurant"
            )

        OrderStateService.validate_transition(
            current_status=order.status,
            new_status=OrderStatus.RESTAURANT_ACCEPTED,
        )

        order.status = OrderStatus.RESTAURANT_ACCEPTED
        self.order_notification_service.notify_status_change(
            user_id=order.user_id,
            order_id=order.id,
            status=order.status,
        )
        self.db.commit()
        self.db.refresh(order)

        return order
    
    def reject_order(
        self,
        order_id: int,
        owner_id: int,
    ):
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise NotFoundError("Order not found")

        restaurant = self.restaurant_repository.get_by_id(
            order.restaurant_id
        )

        if restaurant is None:
            raise NotFoundError("Restaurant not found")

        if restaurant.owner_id != owner_id:
            raise ForbiddenError(
                "You do not own this restaurant"
            )

        OrderStateService.validate_transition(
            current_status=order.status,
            new_status=OrderStatus.CANCELLED,
        )

        order.status = OrderStatus.CANCELLED

        self.db.commit()
        self.db.refresh(order)

        return order
    
    def update_restaurant_order_status(
        self,
        order_id: int,
        owner_id: int,
        new_status: str,
    ):
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise NotFoundError("Order not found")

        restaurant = self.restaurant_repository.get_by_id(
            order.restaurant_id
        )

        if restaurant is None:
            raise NotFoundError("Restaurant not found")

        if restaurant.owner_id != owner_id:
            raise ForbiddenError(
                "You do not own this restaurant"
            )

        allowed_statuses = {
            OrderStatus.PREPARING,
            OrderStatus.READY_FOR_PICKUP,
        }

        if new_status not in allowed_statuses:
            raise ValidationError(
                "Invalid restaurant order status"
            )

        OrderStateService.validate_transition(
            current_status=order.status,
            new_status=new_status,
        )

        order.status = new_status

        self.order_notification_service.notify_status_change(
            user_id=order.user_id,
            order_id=order.id,
            status=order.status,
        )
        
        self.db.commit()
        self.db.refresh(order)

        return order
    
    def get_order_for_restaurant(
        self,
        order_id: int,
        owner_id: int,
    ):
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise NotFoundError("Order not found")

        restaurant = self.restaurant_repository.get_by_id(
            order.restaurant_id
        )

        if restaurant is None:
            raise NotFoundError("Restaurant not found")

        if restaurant.owner_id != owner_id:
            raise ForbiddenError(
                "You do not own this restaurant"
            )

        return order
    
    