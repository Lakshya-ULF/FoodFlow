from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import bearer_scheme, decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:

    payload = decode_access_token(credentials.credentials)

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    repository = UserRepository(db)

    user = repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    return user


def require_role(required_role: str):

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker