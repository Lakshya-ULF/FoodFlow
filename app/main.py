from fastapi import FastAPI
from sqlalchemy import text
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.auth import router as auth_router
from app.core.config import settings
from app.db.session import engine
from app.api.users import router as users_router
from app.api.restaurants import router as restaurant_router
from app.api.menu import router as menu_router
from app.api.cart import router as cart_router
from app.api.orders import router as order_router
from app.api.delivery_partners import (
    router as delivery_router,
)
from app.api.benchmark import router as benchmark_router
from app.api.notifications import router as notification_router
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.search import router as search_router

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    InvalidStateTransitionError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.middleware.request_id import RequestIDMiddleware
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.app_name,
)
Instrumentator().instrument(app).expose(app)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(restaurant_router)
app.include_router(menu_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(delivery_router)
app.include_router(notification_router)
app.include_router(search_router)
app.include_router(benchmark_router)
app.add_middleware(RequestIDMiddleware)

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": result.scalar(),
    }
    
@app.exception_handler(NotFoundError)
async def not_found_handler(
    request: Request,
    exc: NotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(
    request: Request,
    exc: UnauthorizedError,
):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
    )


@app.exception_handler(ForbiddenError)
async def forbidden_handler(
    request: Request,
    exc: ForbiddenError,
):
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc)},
    )


@app.exception_handler(ValidationError)
async def validation_handler(
    request: Request,
    exc: ValidationError,
):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(ConflictError)
async def conflict_handler(
    request: Request,
    exc: ConflictError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidStateTransitionError)
async def invalid_state_transition_handler(
    request: Request,
    exc: InvalidStateTransitionError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )