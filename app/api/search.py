from fastapi import APIRouter, Query

from app.services.restaurant_search_service import RestaurantSearchService


router = APIRouter(
    prefix="/api/v1/search",
    tags=["Search"],
)


@router.get("/restaurants")
def search_restaurants(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    service = RestaurantSearchService()

    return service.search(
        query=q,
        limit=limit,
        offset=offset,
    )
    
@router.get("/menu")
def search_menu(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    service = RestaurantSearchService()

    return service.search_menu(
        query=q,
        limit=limit,
        offset=offset,
    )