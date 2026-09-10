from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.cart import (
    CartItemCreateRequest,
    CartItemUpdateRequest,
    CartResponse,
)
from app.services.cart_service import CartService


router = APIRouter(
    prefix="/api/v1/cart",
    tags=["Cart"],
)


@router.get(
    "",
    response_model=CartResponse,
)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CartService(db)

    return service.get_cart(current_user.id)


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
)
def add_item(
    request: CartItemCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CartService(db)

    try:
        item = service.add_item(
            user_id=current_user.id,
            menu_item_id=request.menu_item_id,
            quantity=request.quantity,
        )

        return {
            "message": "Item added to cart",
            "item_id": item.id,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.put(
    "/items/{menu_item_id}",
)
def update_item(
    menu_item_id: int,
    request: CartItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CartService(db)

    try:
        item = service.update_quantity(
            user_id=current_user.id,
            menu_item_id=menu_item_id,
            quantity=request.quantity,
        )

        return {
            "message": "Cart item updated",
            "item_id": item.id,
            "quantity": item.quantity,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/items/{menu_item_id}",
)
def remove_item(
    menu_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CartService(db)

    try:
        service.remove_item(
            user_id=current_user.id,
            menu_item_id=menu_item_id,
        )

        return {
            "message": "Item removed from cart",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "",
)
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CartService(db)

    service.clear_cart(current_user.id)

    return {
        "message": "Cart cleared",
    }