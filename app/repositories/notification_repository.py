from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        order_id: int,
        notification_type: str,
        message: str,
    ):
        notification = Notification(
            user_id=user_id,
            order_id=order_id,
            type=notification_type,
            message=message,
            is_read=False,
        )

        self.db.add(notification)
        self.db.flush()

        return notification

    def get_by_user(self, user_id: int):
        statement = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.id.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(self, notification_id: int):
        statement = select(Notification).where(
            Notification.id == notification_id
        )

        return self.db.scalar(statement)

    def mark_as_read(self, notification):
        notification.is_read = True
        self.db.flush()

        return notification