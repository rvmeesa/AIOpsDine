from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.orders import OrderCreateRequest, OrderUpdateRequest, OrderResponse
from app.services.order_agent.service import create_order, update_order_status
from db.connection import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/orders/create", response_model=OrderResponse)
async def create_order_endpoint(request: OrderCreateRequest, db: Session = Depends(get_db)):
    try:
        result = await create_order(db, request.table_id, request.items)
        logger.info(f"Order created: {result}")
        return OrderResponse(**result)
    except ValueError as ve:
        logger.error(f"Order creation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Order creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/orders/update", response_model=OrderResponse)
async def update_order_endpoint(request: OrderUpdateRequest, db: Session = Depends(get_db)):
    try:
        result = await update_order_status(db, request.order_id, request.status)
        logger.info(f"Order updated: {result}")
        return OrderResponse(**result)
    except ValueError as ve:
        logger.error(f"Order update error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Order update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))