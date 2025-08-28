from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.connection import get_db
import logging
from sqlalchemy.sql import text

router = APIRouter(prefix="/api/tables")
logger = logging.getLogger(__name__)

@router.get("")
async def get_tables(db: Session = Depends(get_db)):
    try:
        tables = db.execute(
            text("SELECT id, capacity, status FROM tables")
        ).fetchall()
        return [{"id": row[0], "capacity": row[1], "status": row[2]} for row in tables]
    except Exception as e:
        logger.error(f"Failed to fetch tables: {str(e)}")
        raise