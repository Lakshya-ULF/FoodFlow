from fastapi import APIRouter, Query

from app.repositories.restaurant_repository import RestaurantRepository
from app.core.cache import Cache
from app.db.session import SessionLocal
from app.repositories.restaurant_repository import RestaurantRepository

router = APIRouter(prefix="/api/v1/benchmark", tags=["benchmark"])

CACHE_KEY = "benchmark:restaurants:active"
CACHE_TTL = 300


@router.get("/restaurants/db")
def benchmark_db(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    db = SessionLocal()

    try:
        repository = RestaurantRepository(db)

        restaurants = repository.get_all_active(
            limit=limit,
            offset=offset,
        )

        return [
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "owner_id": restaurant.owner_id,
                "is_active": restaurant.is_active,
            }
            for restaurant in restaurants
        ]

    finally:
        db.close()


@router.get("/restaurants/cache")
def benchmark_cache(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    cache_key = f"{CACHE_KEY}:{limit}:{offset}"

    cached = Cache.get(cache_key)

    if cached is not None:
        return cached

    db = SessionLocal()

    try:
        repository = RestaurantRepository(db)

        restaurants = repository.get_all_active(
            limit=limit,
            offset=offset,
        )

        result = [
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "owner_id": restaurant.owner_id,
                "is_active": restaurant.is_active,
            }
            for restaurant in restaurants
        ]

        Cache.set(
            cache_key,
            result,
            ttl=CACHE_TTL,
        )

        return result

    finally:
        db.close()