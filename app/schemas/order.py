from decimal import Decimal

from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    item_name: str
    unit_price: Decimal
    quantity: int

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    status: str
    payment_status: str
    total_amount: Decimal
    items: list[OrderItemResponse]
    
class OrderStatusUpdateRequest(BaseModel):
    status: str