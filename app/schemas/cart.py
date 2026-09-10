from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemCreateRequest(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0)


class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    menu_item_id: int
    name: str
    price: Decimal
    quantity: int


class CartResponse(BaseModel):
    id: int | None
    user_id: int
    items: list[CartItemResponse]