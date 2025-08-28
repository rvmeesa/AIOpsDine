import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session
from app.services.order_agent.service import create_order, update_order_status
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_create_order():
    """Test Order Agent's create_order with valid table."""
    mock_db = AsyncMock(spec=Session)
    mock_db.execute.side_effect = [
        AsyncMock(fetchone=lambda: ("detected_empty",)),  # Vision event
        AsyncMock(fetchone=lambda: (1,))  # Order ID
    ]
    
    with patch("app.services.order_agent.service.parse_order_text", new=AsyncMock(return_value=[])):
        result = await create_order(mock_db, table_id=1, items=[{"menu_id": 1, "qty": 2}])
        
        logger.info(f"Test create_order: {result}")
        assert result["order_id"] == 1
        assert result["status"] == "pending"
        mock_db.execute.assert_called()
        mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_order_status():
    """Test Order Agent's update_order_status."""
    mock_db = AsyncMock(spec=Session)
    result = await update_order_status(mock_db, order_id=1, new_status="served")
    
    logger.info(f"Test update_order_status: {result}")
    assert result["order_id"] == 1
    assert result["status"] == "served"
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()