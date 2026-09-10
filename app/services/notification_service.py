from sqlalchemy.orm import Session

from app.repositories.notification_repository import (
    NotificationRepository,
)

from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
)

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_repository = NotificationRepository(db)

    def create_notification(
        self,
        user_id: int,
        order_id: int,
        notification_type: str,
        message: str,
    ):
        return self.notification_repository.create(
            user_id=user_id,
            order_id=order_id,
            notification_type=notification_type,
            message=message,
        )

    def get_user_notifications(self, user_id: int):
        return self.notification_repository.get_by_user(user_id)

    def mark_as_read(
        self,
        notification_id: int,
        user_id: int,
    ):
        notification = self.notification_repository.get_by_id(
            notification_id
        )

        if notification is None:
            raise NotFoundError("Notification not found")

        if notification.user_id != user_id:
            raise ForbiddenError(
                "You do not have access to this notification"
            )

        notification = self.notification_repository.mark_as_read(
            notification
        )

        self.db.commit()
        self.db.refresh(notification)

        return notification