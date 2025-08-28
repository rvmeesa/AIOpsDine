from pydantic import BaseModel
from typing import List

class RecoRequest(BaseModel):
    order_id: int

class RecoResponse(BaseModel):
    suggestions: List[dict]  # e.g., [{"item_id": int, "uplift": float}]