from app.db.session import SessionLocal

db = SessionLocal()

from app.services.notification_service import NotificationService

service = NotificationService(db)

notification = service.create_notification(
    user_id=1,
    order_id=6,
    notification_type="order_update",
    message="Your order has been accepted",
)