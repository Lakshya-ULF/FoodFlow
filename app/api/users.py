from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse
from app.models.user import User

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user