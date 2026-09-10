from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository


class UserService:

    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def register_user(
        self,
        email: str,
        password: str,
    ):
        existing_user = self.user_repository.get_by_email(email)

        if existing_user:
            raise ValueError("User with this email already exists")

        password_hash = hash_password(password)

        user = self.user_repository.create(
            email=email,
            password_hash=password_hash,
        )

        self.user_repository.db.commit()
        self.user_repository.db.refresh(user)

        return user

    def login_user(
        self,
        email: str,
        password: str,
    ) -> str:

        user = self.user_repository.get_by_email(email)

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        return create_access_token(
            user_id=user.id,
            role=user.role,
        )