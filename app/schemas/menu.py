from decimal import Decimal

from pydantic import BaseModel, Field


class MenuItemCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )


class MenuItemUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )


class MenuItemResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: str | None
    price: Decimal
    is_available: bool

    model_config = {
        "from_attributes": True
    }