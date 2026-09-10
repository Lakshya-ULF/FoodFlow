from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.restaurant import (
    RestaurantCreateRequest,
    RestaurantResponse,
    RestaurantUpdateRequest,
)
from app.services.restaurant_service import RestaurantService
from app.core.constants import UserRole

router = APIRouter(
    prefix="/api/v1/restaurants",
    tags=["Restaurants"],
)


@router.get(
    "",
    response_model=list[RestaurantResponse],
)
def list_restaurants(
    db: Session = Depends(get_db),
):
    service = RestaurantService(db)

    return service.get_active_restaurants()


@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    service = RestaurantService(db)

    try:
        return service.get_restaurant(restaurant_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_restaurant(
    request: RestaurantCreateRequest,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = RestaurantService(db)

    return service.create_restaurant(
        name=request.name,
        address=request.address,
        owner_id=current_user.id,
    )


@router.get(
    "/owner/me",
    response_model=list[RestaurantResponse],
)
def get_my_restaurants(
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = RestaurantService(db)

    return service.get_owner_restaurants(
        owner_id=current_user.id,
    )


@router.put(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
def update_restaurant(
    restaurant_id: int,
    request: RestaurantUpdateRequest,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = RestaurantService(db)

    try:
        return service.update_restaurant(
            restaurant_id=restaurant_id,
            owner_id=current_user.id,
            name=request.name,
            address=request.address,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.patch(
    "/{restaurant_id}/status",
    response_model=RestaurantResponse,
)
def set_restaurant_status(
    restaurant_id: int,
    is_active: bool,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = RestaurantService(db)

    try:
        return service.set_restaurant_active(
            restaurant_id=restaurant_id,
            owner_id=current_user.id,
            is_active=is_active,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )