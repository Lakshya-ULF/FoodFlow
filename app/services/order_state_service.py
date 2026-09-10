from app.core.constants import OrderStatus
from app.core.exceptions import InvalidStateTransitionError


ALLOWED_TRANSITIONS = {
    OrderStatus.CREATED: {
        OrderStatus.PAYMENT_PENDING,
        OrderStatus.CANCELLED,
    },
    OrderStatus.PAYMENT_PENDING: {
        OrderStatus.PAID,
        OrderStatus.PAYMENT_FAILED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.PAID: {
        OrderStatus.RESTAURANT_ACCEPTED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.RESTAURANT_ACCEPTED: {
        OrderStatus.PREPARING,
    },
    OrderStatus.PREPARING: {
        OrderStatus.READY_FOR_PICKUP,
    },
    OrderStatus.READY_FOR_PICKUP: {
        OrderStatus.PICKED_UP,
    },
    OrderStatus.PICKED_UP: {
        OrderStatus.OUT_FOR_DELIVERY,
    },
    OrderStatus.OUT_FOR_DELIVERY: {
        OrderStatus.DELIVERED,
    },
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
    OrderStatus.PAYMENT_FAILED: set(),
}


class OrderStateService:

    @staticmethod
    def validate_transition(
        current_status: str,
        new_status: str,
    ) -> None:

        allowed = ALLOWED_TRANSITIONS.get(current_status, set())

        if new_status not in allowed:
            raise InvalidStateTransitionError(
                f"Invalid order transition: "
                f"{current_status} -> {new_status}"
            )