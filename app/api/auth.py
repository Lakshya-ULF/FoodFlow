from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserRegisterRequest, UserResponse
from app.services.user_service import UserService

from app.schemas.user import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
):
    service = UserService(db)

    try:
        access_token = service.login_user(
            email=request.email,
            password=request.password,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    service = UserService(db)

    try:
        return service.register_user(
            email=request.email,
            password=request.password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )