from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.outbox_event import OutboxEvent


class OutboxRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        event_type: str,
        payload: str,
    ) -> OutboxEvent:

        event = OutboxEvent(
            event_type=event_type,
            payload=payload,
            status="pending",
        )

        self.db.add(event)
        self.db.flush()

        return event

    def get_pending(self, limit: int = 10) -> list[OutboxEvent]:

        statement = (
            select(OutboxEvent)
            .where(OutboxEvent.status == "pending")
            .order_by(OutboxEvent.id)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())