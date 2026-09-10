from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.constants import OrderStatus, PaymentStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    ValidationError,
)

class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.payment_repository = PaymentRepository(db)
        self.order_repository = OrderRepository(db)

    def create_payment(
        self,
        order_id: int,
        user_id: int,
        idempotency_key: str,
    ):
        # 1. Idempotency check
        existing_payment = (
            self.payment_repository.get_by_idempotency_key(
                idempotency_key
            )
        )

        if existing_payment is not None:
            return existing_payment

        # 2. Verify order
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise NotFoundError("Order not found")

        if order.user_id != user_id:
            raise ForbiddenError(
                "You do not have access to this order"
            )

        if order.status != OrderStatus.PAYMENT_PENDING:
            raise ValidationError(
                "Order is not awaiting payment"
            )

        # 3. Create payment
        # 3. Create payment
        try:
            payment = self.payment_repository.create(
                order_id=order.id,
                amount=Decimal(str(order.total_amount)),
                idempotency_key=idempotency_key,
                status=PaymentStatus.PENDING,
            )

            self.db.commit()

        except IntegrityError:
            self.db.rollback()

            # Another concurrent request may have created
            # the payment with the same idempotency key.
            existing_payment = (
                self.payment_repository.get_by_idempotency_key(
                    idempotency_key
                )
            )

            if existing_payment is not None:
                return existing_payment

            raise

        self.db.refresh(payment)

        return payment
    
    def process_payment_result(
        self,
        payment_id: int,
        success: bool,
    ):
        payment = self.payment_repository.get_by_id(payment_id)

        if payment is None:
            raise NotFoundError("Payment not found")

        order = self.order_repository.get_by_id(
            payment.order_id
        )

        if order is None:
            raise NotFoundError("Order not found")

        # Duplicate callback: payment is already finalized.
        if payment.status in (
            PaymentStatus.SUCCESS,
            PaymentStatus.FAILED,
        ):
            return payment

        if success:
            payment.status = PaymentStatus.SUCCESS

            order.payment_status = PaymentStatus.SUCCESS
            order.status = OrderStatus.PAID

        else:
            payment.status = PaymentStatus.FAILED

            order.payment_status = PaymentStatus.FAILED
            order.status = OrderStatus.PAYMENT_FAILED

        self.db.commit()

        self.db.refresh(payment)

        return payment
    
    
    def get_payment_for_order(
        self,
        payment_id: int,
        order_id: int,
    ):
        payment = self.payment_repository.get_by_id(payment_id)

        if payment is None:
            raise NotFoundError("Payment not found")

        if payment.order_id != order_id:
            raise ValidationError(
                "Payment does not belong to this order"
            )

        return payment