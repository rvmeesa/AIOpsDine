from pydantic import BaseModel
from typing import List

class TopItem(BaseModel):
    menu_id: int
    name: str
    quantity: int

class AnalyticsResponse(BaseModel):
    total_orders: int
    total_revenue: float
    top_items: List[TopItem]
    avg_ticket_size: float