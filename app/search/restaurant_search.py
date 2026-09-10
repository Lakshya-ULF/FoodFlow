from app.core.elasticsearch import elasticsearch_client
from app.repositories.restaurant_repository import RestaurantRepository


RESTAURANT_INDEX = "restaurants"


def create_restaurant_index():
    if elasticsearch_client.indices.exists(index=RESTAURANT_INDEX):
        return

    elasticsearch_client.indices.create(
        index=RESTAURANT_INDEX,
        mappings={
            "properties": {
                "id": {"type": "integer"},
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "address": {"type": "text"},
                "owner_id": {"type": "integer"},
                "is_active": {"type": "boolean"},
            }
        },
    )


def index_restaurant(restaurant):
    document = {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "owner_id": restaurant.owner_id,
        "is_active": restaurant.is_active,
    }

    elasticsearch_client.index(
        index=RESTAURANT_INDEX,
        id=restaurant.id,
        document=document,
    )


def search_restaurants(
    query: str,
    limit: int = 10,
):
    response = elasticsearch_client.search(
        index=RESTAURANT_INDEX,
        query={
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "name",
                                "address",
                            ],
                        }
                    }
                ],
                "filter": [
                    {
                        "term": {
                            "is_active": True
                        }
                    }
                ],
            }
        },
        size=limit,
    )

    return [
        hit["_source"]
        for hit in response["hits"]["hits"]
    ]