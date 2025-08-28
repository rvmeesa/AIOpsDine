from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.orchestrator import assign_table_to_reservation
from db.connection import get_db

router = APIRouter()

class TableAssignRequest(BaseModel):
    table_id: int

@router.post("/table-assign")
async def assign_table(request: TableAssignRequest, db=Depends(get_db)):
    result = await assign_table_to_reservation(request.table_id)
    if result:
        return result
    return {"error": "Table assignment failed"}