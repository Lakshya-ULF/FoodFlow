from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.delivery_assignment import DeliveryAssignment


class DeliveryAssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_order_id(
        self,
        order_id: int,
    ) -> DeliveryAssignment | None:
        statement = select(DeliveryAssignment).where(
            DeliveryAssignment.order_id == order_id
        )

        return self.db.scalar(statement)

    def get_by_partner_id(
        self,
        delivery_partner_id: int,
    ) -> list[DeliveryAssignment]:
        statement = (
            select(DeliveryAssignment)
            .where(
                DeliveryAssignment.delivery_partner_id
                == delivery_partner_id
            )
            .order_by(DeliveryAssignment.id.desc())
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        order_id: int,
        delivery_partner_id: int,
    ) -> DeliveryAssignment:
        assignment = DeliveryAssignment(
            order_id=order_id,
            delivery_partner_id=delivery_partner_id,
            status="assigned",
        )

        self.db.add(assignment)
        self.db.flush()

        return assignment

    def update_status(
        self,
        assignment: DeliveryAssignment,
        status: str,
    ) -> DeliveryAssignment:
        assignment.status = status

        self.db.flush()

        return assignment