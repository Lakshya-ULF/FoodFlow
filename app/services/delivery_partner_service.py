from sqlalchemy.orm import Session

from app.repositories.delivery_partner_repository import (
    DeliveryPartnerRepository,
)


class DeliveryPartnerService:
    def __init__(self, db: Session):
        self.db = db

        self.repository = DeliveryPartnerRepository(db)

    def get_or_create_profile(
        self,
        user_id: int,
    ):
        partner = self.repository.get_by_user_id(user_id)

        if partner is not None:
            return partner

        partner = self.repository.create(user_id)

        self.db.commit()
        self.db.refresh(partner)

        return partner

    def set_online_status(
        self,
        user_id: int,
        is_online: bool,
    ):
        partner = self.repository.get_by_user_id(user_id)

        if partner is None:
            raise ValueError(
                "Delivery partner profile not found"
            )

        partner = self.repository.set_online(
            partner=partner,
            is_online=is_online,
        )

        self.db.commit()
        self.db.refresh(partner)

        return partner