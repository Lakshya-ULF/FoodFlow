from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.delivery_partner import DeliveryPartner


class DeliveryPartnerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(
        self,
        user_id: int,
    ) -> DeliveryPartner | None:
        statement = select(DeliveryPartner).where(
            DeliveryPartner.user_id == user_id
        )

        return self.db.scalar(statement)

    def get_by_id(
        self,
        partner_id: int,
    ) -> DeliveryPartner | None:
        statement = select(DeliveryPartner).where(
            DeliveryPartner.id == partner_id
        )

        return self.db.scalar(statement)

    def create(
        self,
        user_id: int,
    ) -> DeliveryPartner:
        partner = DeliveryPartner(
            user_id=user_id,
            is_online=False,
        )

        self.db.add(partner)
        self.db.flush()

        return partner

    def set_online(
        self,
        partner: DeliveryPartner,
        is_online: bool,
    ) -> DeliveryPartner:
        partner.is_online = is_online

        self.db.flush()

        return partner

    def get_online_partners(self) -> list[DeliveryPartner]:
        statement = (
            select(DeliveryPartner)
            .where(
                DeliveryPartner.is_online.is_(True)
            )
            .order_by(DeliveryPartner.id)
        )

        return list(self.db.scalars(statement).all())