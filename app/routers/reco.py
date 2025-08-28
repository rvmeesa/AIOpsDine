from fastapi import APIRouter, HTTPException
from app.schemas.reco import RecoRequest, RecoResponse
from app.services.reco_agent.service import get_recommendations
import logging

router = APIRouter(prefix="/api/reco", tags=["recommendations"])
logger = logging.getLogger(__name__)

@router.post("/suggest", response_model=RecoResponse)
async def suggest_endpoint(request: RecoRequest):
    logger.info(f"Received request for order_id: {request.order_id}")  # Add this
    try:
        suggestions = await get_recommendations(request.order_id)
        logger.info(f"Suggestions for order {request.order_id}: {suggestions}")
        return RecoResponse(suggestions=suggestions)
    except Exception as e:
        logger.error(f"Recommendation suggestion error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))