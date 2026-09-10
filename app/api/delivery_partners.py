from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.core.constants import UserRole
from app.db.session import get_db
from app.models.user import User
from app.services.delivery_partner_service import (
    DeliveryPartnerService,
)


router = APIRouter(
    prefix="/api/v1/delivery",
    tags=["Delivery"],
)


@router.post(
    "/profile",
)
def create_profile(
    current_user: User = Depends(
        require_role(UserRole.DELIVERY_PARTNER)
    ),
    db: Session = Depends(get_db),
):
    service = DeliveryPartnerService(db)

    return service.get_or_create_profile(
        current_user.id
    )


@router.patch(
    "/status",
)
def set_online_status(
    is_online: bool,
    current_user: User = Depends(
        require_role(UserRole.DELIVERY_PARTNER)
    ),
    db: Session = Depends(get_db),
):
    service = DeliveryPartnerService(db)

    try:
        return service.set_online_status(
            user_id=current_user.id,
            is_online=is_online,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )