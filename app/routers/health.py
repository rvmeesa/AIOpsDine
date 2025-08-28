from fastapi import APIRouter, Depends
from datetime import datetime
import asyncio
from app.orchestrator import event_queue
import logging

from app.schemas.health import HealthResponse
from db.connection import engine  # Step 2 file; engine is SQLAlchemy engine

router = APIRouter()
logger = logging.getLogger("ai_restaurant.health")

def _check_db_sync():
    """
    Sync function that attempts to connect to the DB using SQLAlchemy engine.
    Keep lightweight — we'll call it in a thread via asyncio.to_thread to avoid blocking.
    """
    with engine.connect() as conn:
        # Quick, harmless query that works across DB backends
        res = conn.execute("SELECT 1")
        # consume / ensure query was executed
        _ = res.fetchone()
    return True

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Returns a JSON object indicating API and DB health.
    Example response:
    {
      "status": "ok",
      "db_connected": true,
      "timestamp": "2025-08-16T12:34:56.789Z",
      "message": "OK"
    }
    """
    db_ok = False
    try:
        # run the DB check in a thread to keep the event loop free
        db_ok = await asyncio.to_thread(_check_db_sync)
    except Exception as e:
        logger.warning("DB connectivity check failed: %s", e)
        db_ok = False

    status = "ok" if db_ok else "degraded"
    msg = None if db_ok else "Database connection failed. Check DB_URL and that restaurant.db exists."
    return HealthResponse(
        status=status,
        db_connected=db_ok,
        timestamp=datetime.utcnow(),
        message=msg
    )

@router.get("/orchestrator-status")
async def orchestrator_status():
    return {"queue_size": event_queue.qsize(), "status": "running"}