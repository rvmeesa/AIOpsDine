from pydantic import BaseModel

class TableAssignRequest(BaseModel):
    table_id: int

class TableAssignResponse(BaseModel):
    table_id: int
    order_id: int
    reservation_id: int | None = None