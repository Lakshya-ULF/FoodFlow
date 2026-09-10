from pydantic import BaseModel, Field


class RestaurantCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    address: str = Field(min_length=5, max_length=500)


class RestaurantUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    address: str = Field(min_length=5, max_length=500)


class RestaurantResponse(BaseModel):
    id: int
    name: str
    address: str
    owner_id: int
    is_active: bool

    model_config = {
        "from_attributes": True
    }