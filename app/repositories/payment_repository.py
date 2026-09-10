from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Payment | None:
        statement = select(Payment).where(
            Payment.idempotency_key == idempotency_key
        )

        return self.db.scalar(statement)

    def get_by_order_id(self, order_id: int) -> Payment | None:
        statement = select(Payment).where(
            Payment.order_id == order_id
        )

        return self.db.scalar(statement)

    def create(
        self,
        order_id: int,
        amount,
        idempotency_key: str,
        status: str,
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            amount=amount,
            idempotency_key=idempotency_key,
            status=status,
        )

        self.db.add(payment)
        self.db.flush()

        return payment
    
    def get_by_id(self, payment_id: int) -> Payment | None:
        statement = select(Payment).where(
            Payment.id == payment_id
        )

        return self.db.scalar(statement)