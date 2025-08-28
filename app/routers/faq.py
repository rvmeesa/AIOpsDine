from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.faq_agent.service import answer_query
from sqlalchemy.orm import Session
from db.connection import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class FAQRequest(BaseModel):
    query: str

class FAQResponse(BaseModel):
    response: str

@router.post("/query", response_model=FAQResponse)
async def faq_query(request: FAQRequest, db: Session = Depends(get_db)):
    try:
        response = await answer_query(request.query)
        logger.info(f"Processed FAQ query: {request.query}")
        return FAQResponse(response=response)
    except Exception as e:
        logger.error(f"FAQ query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"FAQ query failed: {str(e)}")