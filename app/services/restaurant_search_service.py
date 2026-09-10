from app.search.restaurant_search import search_restaurants
from app.search.menu_search import search_menu_items

class RestaurantSearchService:

    def search(
        self,
        query: str,
        limit: int = 10,
    ):
        return search_restaurants(
            query=query,
            limit=limit,
        )
        
    def search_menu(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ):
        return search_menu_items(
            query=query,
            limit=limit,
            offset=offset,
        )