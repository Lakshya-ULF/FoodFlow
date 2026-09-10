from app.core.elasticsearch import elasticsearch_client


MENU_INDEX = "menu_items"


def create_menu_index():
    if elasticsearch_client.indices.exists(index=MENU_INDEX):
        return

    elasticsearch_client.indices.create(
        index=MENU_INDEX,
        mappings={
            "properties": {
                "id": {"type": "integer"},
                "restaurant_id": {"type": "integer"},
                "restaurant_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    },
                },
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    },
                },
                "description": {"type": "text"},
                "price": {"type": "float"},
                "is_available": {"type": "boolean"},
                "restaurant_is_active": {"type": "boolean"},
            }
        },
    )


def index_menu_item(menu_item, restaurant):
    document = {
        "id": menu_item.id,
        "restaurant_id": menu_item.restaurant_id,
        "restaurant_name": restaurant.name,
        "name": menu_item.name,
        "description": menu_item.description,
        "price": float(menu_item.price),
        "is_available": menu_item.is_available,
        "restaurant_is_active": restaurant.is_active,
    }

    elasticsearch_client.index(
        index=MENU_INDEX,
        id=menu_item.id,
        document=document,
    )
    
def index_existing_menu_items(db):
    from app.models.main_menu import MenuItem
    from app.models.restaurant import Restaurant

    items = (
        db.query(MenuItem, Restaurant)
        .join(
            Restaurant,
            MenuItem.restaurant_id == Restaurant.id,
        )
        .all()
    )

    for menu_item, restaurant in items:
        index_menu_item(menu_item, restaurant)

def search_menu_items(
    query: str,
    limit: int = 10,
    offset: int = 0,
):
    response = elasticsearch_client.search(
        index=MENU_INDEX,
        query={
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "name^3",
                                "description",
                                "restaurant_name^2",
                            ],
                        }
                    }
                ],
                "filter": [
                    {
                        "term": {
                            "is_available": True
                        }
                    },
                    {
                        "term": {
                            "restaurant_is_active": True
                        }
                    },
                ],
            }
        },
        from_=offset,
        size=limit,
    )

    return {
        "total": response["hits"]["total"]["value"],
        "results": [
            hit["_source"]
            for hit in response["hits"]["hits"]
        ],
    }