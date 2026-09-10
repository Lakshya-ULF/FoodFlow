class UserRole:
    CUSTOMER = "customer"
    RESTAURANT_OWNER = "restaurant_owner"
    DELIVERY_PARTNER = "delivery_partner"
    ADMIN = "admin"
    
class OrderStatus:
    CREATED = "created"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    RESTAURANT_ACCEPTED = "restaurant_accepted"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    PICKED_UP = "picked_up"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    PAYMENT_FAILED = "payment_failed"


class PaymentStatus:
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    
class OutboxStatus:
    PENDING = "pending"
    PUBLISHED = "published"
    DEAD_LETTER = "dead_letter"

    MAX_RETRIES = 5