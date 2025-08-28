from pydantic import BaseModel
from typing import List, Optional

class OrderItem(BaseModel):
    menu_id: int
    quantity: Optional[int] = 1

class OrderCreateRequest(BaseModel):
    table_id: int
    items: List[OrderItem]

class OrderUpdateRequest(BaseModel):
    order_id: int
    status: str

class OrderResponse(BaseModel):
    order_id: int
    table_id: int
    status: str
    items: Optional[List[OrderItem]] = None