from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService


router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    return service.get_user_notifications(
        user_id=current_user.id
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    return service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )