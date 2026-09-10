from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.core.constants import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.menu import (
    MenuItemCreateRequest,
    MenuItemResponse,
    MenuItemUpdateRequest,
)
from app.services.menu_service import MenuService


router = APIRouter(
    prefix="/api/v1",
    tags=["Menu"],
)


@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=list[MenuItemResponse],
)
def get_menu(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    service = MenuService(db)

    try:
        return service.get_menu(restaurant_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/restaurants/{restaurant_id}/menu/available",
    response_model=list[MenuItemResponse],
)
def get_available_menu(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    service = MenuService(db)

    try:
        return service.get_available_menu(restaurant_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_menu_item(
    restaurant_id: int,
    request: MenuItemCreateRequest,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = MenuService(db)

    try:
        return service.create_item(
            restaurant_id=restaurant_id,
            owner_id=current_user.id,
            name=request.name,
            description=request.description,
            price=request.price,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.put(
    "/menu/{item_id}",
    response_model=MenuItemResponse,
)
def update_menu_item(
    item_id: int,
    request: MenuItemUpdateRequest,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = MenuService(db)

    try:
        return service.update_item(
            item_id=item_id,
            owner_id=current_user.id,
            name=request.name,
            description=request.description,
            price=request.price,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.patch(
    "/menu/{item_id}/availability",
    response_model=MenuItemResponse,
)
def set_menu_item_availability(
    item_id: int,
    is_available: bool,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = MenuService(db)

    try:
        return service.set_item_available(
            item_id=item_id,
            owner_id=current_user.id,
            is_available=is_available,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )