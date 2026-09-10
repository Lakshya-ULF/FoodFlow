import json

from app.core.constants import OrderStatus
from app.repositories.outbox_repository import OutboxRepository


class OrderNotificationService:

    def __init__(self, db):
        self.outbox_repository = OutboxRepository(db)

    def notify_status_change(
        self,
        user_id: int,
        order_id: int,
        status: str,
    ):
        messages = {
            OrderStatus.PAID: "Your payment was successful.",
            OrderStatus.RESTAURANT_ACCEPTED: (
                "Your order has been accepted by the restaurant."
            ),
            OrderStatus.PREPARING: (
                "Your order is being prepared."
            ),
            OrderStatus.READY_FOR_PICKUP: (
                "Your order is ready for pickup."
            ),
            OrderStatus.PICKED_UP: (
                "Your order has been picked up by the delivery partner."
            ),
            OrderStatus.OUT_FOR_DELIVERY: (
                "Your order is out for delivery."
            ),
            OrderStatus.DELIVERED: (
                "Your order has been delivered."
            ),
            OrderStatus.CANCELLED: (
                "Your order has been cancelled."
            ),
            OrderStatus.PAYMENT_FAILED: (
                "Your payment failed."
            ),
        }

        message = messages.get(status)

        if message is None:
            return None

        payload = {
            "user_id": user_id,
            "order_id": order_id,
            "type": "order_status",
            "status": status,
            "message": message,
        }

        return self.outbox_repository.create(
            event_type="order_status_notification",
            payload=json.dumps(payload),
        )