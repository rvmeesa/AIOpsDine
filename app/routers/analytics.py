from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_agent.service import compute_kpis
from db.connection import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics_summary(date: str, range_type: str = "daily", db: Session = Depends(get_db)):
    try:
        kpis = await compute_kpis(db, date, range_type)
        logger.info(f"Fetched KPIs for date {date}, range {range_type}: {kpis}")
        return AnalyticsResponse(**kpis)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Analytics fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))