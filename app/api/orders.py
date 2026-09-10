from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.core.constants import UserRole
from app.db.session import get_db
from app.models.user import User
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService

from app.schemas.order import (
    OrderResponse,
    OrderStatusUpdateRequest,
)

from app.services.delivery_assignment_service import (
    DeliveryAssignmentService,
)

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
)


@router.post(
    "/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def checkout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OrderService(db)
    return service.checkout(current_user.id)
        
@router.get(
    "",
    response_model=list[OrderResponse],
)
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OrderService(db)

    return service.get_user_orders(current_user.id)

@router.get(
    "/restaurant/{restaurant_id}",
    response_model=list[OrderResponse],
)
def get_restaurant_orders(
    restaurant_id: int,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = OrderService(db)

    
    return service.get_restaurant_orders(
        restaurant_id=restaurant_id,
        owner_id=current_user.id,
    )

@router.patch(
    "/{order_id}/accept",
    response_model=OrderResponse,
)
def accept_order(
    order_id: int,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = OrderService(db)
    return service.accept_order(
        order_id=order_id,
        owner_id=current_user.id,
    )

@router.patch(
    "/{order_id}/reject",
    response_model=OrderResponse,
)
def reject_order(
    order_id: int,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = OrderService(db)

    
    return service.reject_order(
        order_id=order_id,
        owner_id=current_user.id,
    )


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def update_restaurant_order_status(
    order_id: int,
    request: OrderStatusUpdateRequest,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    service = OrderService(db)

    return service.update_restaurant_order_status(
        order_id=order_id,
        owner_id=current_user.id,
        new_status=request.status,
    )


@router.post(
    "/{order_id}/assign",
)
def assign_delivery_partner(
    order_id: int,
    delivery_partner_id: int,
    current_user: User = Depends(
        require_role(UserRole.RESTAURANT_OWNER)
    ),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)

        # First verify that this restaurant owner owns the order's restaurant.
    order = order_service.get_order_for_restaurant(
        order_id=order_id,
        owner_id=current_user.id,
    )

    assignment_service = DeliveryAssignmentService(db)

    return assignment_service.assign_order(
        order_id=order.id,
        delivery_partner_id=delivery_partner_id,
    )


#before this 
@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OrderService(db)

    return service.get_order(
        order_id=order_id,
        user_id=current_user.id,
    )

@router.post("/{order_id}/payment")
def create_payment(
    order_id: int,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PaymentService(db)

    payment = service.create_payment(
        order_id=order_id,
        user_id=current_user.id,
        idempotency_key=idempotency_key,
    )

    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "status": payment.status,
        "idempotency_key": payment.idempotency_key,
        "provider_reference": payment.provider_reference,
    }
        
@router.post("/{order_id}/payment/callback")
def payment_callback(
    order_id: int,
    payment_id: int,
    success: bool,
    db: Session = Depends(get_db),
):
    service = PaymentService(db)

    service.get_payment_for_order(
        payment_id=payment_id,
        order_id=order_id,
    )

    payment = service.process_payment_result(
        payment_id=payment_id,
        success=success,
    )

    return {
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "status": payment.status,
    }        
        
@router.patch(
    "/{order_id}/delivery/accept",
)
def accept_delivery_assignment(
    order_id: int,
    current_user: User = Depends(
        require_role(UserRole.DELIVERY_PARTNER)
    ),
    db: Session = Depends(get_db),
):
    service = DeliveryAssignmentService(db)

    return service.accept_assignment(
        order_id=order_id,
        user_id=current_user.id,
    )
        
@router.patch(
    "/{order_id}/delivery/pickup",
    response_model=OrderResponse,
)
def pickup_order(
    order_id: int,
    current_user: User = Depends(
        require_role(UserRole.DELIVERY_PARTNER)
    ),
    db: Session = Depends(get_db),
):
    service = DeliveryAssignmentService(db)

    return service.pickup_order(
        order_id=order_id,
        user_id=current_user.id,
    )
        
@router.patch(
    "/{order_id}/delivery/start",
    response_model=OrderResponse,
)
def start_delivery(
    order_id: int,
    current_user: User = Depends(
        require_role(UserRole.DELIVERY_PARTNER)
    ),
    db: Session = Depends(get_db),
):
    service = DeliveryAssignmentService(db)

    return service.start_delivery(
        order_id=order_id,
        user_id=current_user.id,
    )

@router.patch("/{order_id}/delivery/deliver", response_model=OrderResponse)
def deliver_order(
    order_id: int,
    current_user: User = Depends(
        require_role(UserRole.DELIVERY_PARTNER)
    ),
    db: Session = Depends(get_db),
):
    service = DeliveryAssignmentService(db)

    
    return service.deliver_order(
        order_id=order_id,
        user_id=current_user.id,
    )