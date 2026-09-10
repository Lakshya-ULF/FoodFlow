from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.constants import OrderStatus
from app.repositories.delivery_assignment_repository import (
    DeliveryAssignmentRepository,
)
from app.repositories.delivery_partner_repository import (
    DeliveryPartnerRepository,
)
from app.repositories.order_repository import OrderRepository
from app.services.order_state_service import OrderStateService
from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    ValidationError,
    ConflictError
)

from app.services.order_notification_service import (
    OrderNotificationService,
)

class DeliveryAssignmentService:
    def __init__(self, db: Session):
        self.db = db

        self.assignment_repository = (
            DeliveryAssignmentRepository(db)
        )

        self.partner_repository = (
            DeliveryPartnerRepository(db)
        )
        self.order_notification_service = OrderNotificationService(db)
        self.order_repository = OrderRepository(db)

    def assign_order(
        self,
        order_id: int,
        delivery_partner_id: int,
    ):
        # 1. Check order
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise NotFoundError("Order not found")

        # 2. Order must be ready for pickup
        if order.status != OrderStatus.READY_FOR_PICKUP:
            raise ValidationError(
                "Order is not ready for pickup"
            )

        # 3. Check delivery partner
        partner = self.partner_repository.get_by_id(
            delivery_partner_id
        )

        if partner is None:
            raise NotFoundError(
                "Delivery partner not found"
            )

        # 4. Partner must be online
        if not partner.is_online:
            raise ValidationError(
                "Delivery partner is offline"
            )

        # 5. Order must not already be assigned
        existing_assignment = (
            self.assignment_repository.get_by_order_id(
                order_id
            )
        )

        if existing_assignment is not None:
            raise ValidationError(
                "Order is already assigned"
            )

        # 6. Create assignment
        try:
            assignment = self.assignment_repository.create(
                order_id=order_id,
                delivery_partner_id=delivery_partner_id,
                status="assigned",
            )

            self.db.commit()

        except IntegrityError:
            self.db.rollback()

            raise ConflictError(
                "Order already has a delivery assignment"
            )

        self.db.refresh(assignment)

        return assignment
    
    def accept_assignment(
        self,
        order_id: int,
        user_id: int,
    ):
        assignment = (
            self.assignment_repository.get_by_order_id(
                order_id
            )
        )

        if assignment is None:
            raise NotFoundError(
                "Delivery assignment not found"
            )

        partner = self.partner_repository.get_by_id(
            assignment.delivery_partner_id
        )

        if partner is None:
            raise NotFoundError(
                "Delivery partner not found"
            )

        if partner.user_id != user_id:
            raise ForbiddenError(
                "This assignment does not belong to you"
            )

        if assignment.status != "assigned":
            raise ValidationError(
                "Assignment cannot be accepted"
            )

        assignment = self.assignment_repository.update_status(
            assignment=assignment,
            status="accepted",
        )

        self.db.commit()
        self.db.refresh(assignment)

        return assignment
    
    def pickup_order(
        self,
        order_id: int,
        user_id: int,
    ):
        assignment = (
            self.assignment_repository.get_by_order_id(
                order_id
            )
        )

        if assignment is None:
            raise NotFoundError(
                "Delivery assignment not found"
            )

        partner = self.partner_repository.get_by_id(
            assignment.delivery_partner_id
        )

        if partner is None:
            raise NotFoundError(
                "Delivery partner not found"
            )

        if partner.user_id != user_id:
            raise ForbiddenError(
                "This assignment does not belong to you"
            )

        if assignment.status != "accepted":
            raise ValidationError(
                "Delivery assignment has not been accepted"
            )

        order = self.order_repository.get_by_id(
            order_id
        )

        if order is None:
            raise NotFoundError("Order not found")

        OrderStateService.validate_transition(
            current_status=order.status,
            new_status=OrderStatus.PICKED_UP,
        )

        order.status = OrderStatus.PICKED_UP
        assignment.status = "picked_up"

        self.order_notification_service.notify_status_change(
            user_id=order.user_id,
            order_id=order.id,
            status=order.status,
        )
        
        self.db.commit()

        self.db.refresh(order)
        self.db.refresh(assignment)

        return order
    
    def start_delivery(
        self,
        order_id: int,
        user_id: int,
    ):
        assignment = (
            self.assignment_repository.get_by_order_id(
                order_id
            )
        )

        if assignment is None:
            raise NotFoundError(
                "Delivery assignment not found"
            )

        partner = self.partner_repository.get_by_id(
            assignment.delivery_partner_id
        )

        if partner is None:
            raise NotFoundError(
                "Delivery partner not found"
            )

        if partner.user_id != user_id:
            raise ForbiddenError(
                "This assignment does not belong to you"
            )

        if assignment.status != "picked_up":
            raise ValidationError(
                "Order has not been picked up"
            )

        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise NotFoundError("Order not found")

        OrderStateService.validate_transition(
            current_status=order.status,
            new_status=OrderStatus.OUT_FOR_DELIVERY,
        )

        order.status = OrderStatus.OUT_FOR_DELIVERY

        assignment.status = "out_for_delivery"

        self.order_notification_service.notify_status_change(
            user_id=order.user_id,
            order_id=order.id,
            status=order.status,
        )

        self.db.commit()

        self.db.refresh(order)
        self.db.refresh(assignment)

        return order
    
    
    def deliver_order(self, order_id: int, user_id: int):
        assignment = self.assignment_repository.get_by_order_id(order_id)

        if not assignment:
            raise NotFoundError("Delivery assignment not found")

        partner = self.partner_repository.get_by_id(
            assignment.delivery_partner_id
        )

        if not partner or partner.user_id != user_id:
            raise ForbiddenError("You are not assigned to this delivery")

        if assignment.status != "out_for_delivery":
            raise ValidationError("Delivery must be out for delivery")

        order = self.order_repository.get_by_id(order_id)

        if not order:
            raise NotFoundError("Order not found")

        OrderStateService.validate_transition(
            order.status,
            OrderStatus.DELIVERED
        )

        order.status = OrderStatus.DELIVERED
        assignment.status = "delivered"

        self.order_notification_service.notify_status_change(
            user_id=order.user_id,
            order_id=order.id,
            status=order.status,
        )
        
        self.db.commit()

        self.db.refresh(order)
        self.db.refresh(assignment)

        return order