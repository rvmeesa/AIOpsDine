import pytest
from unittest.mock import AsyncMock
from sqlalchemy.orm import Session
from app.services.analytics_agent.service import compute_kpis
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_compute_kpis_daily():
    """Test Analytics Agent's compute_kpis for daily summary."""
    mock_db = AsyncMock(spec=Session)
    mock_db.execute.side_effect = [
        AsyncMock(fetchall=lambda: [(10, 200.0)]),  # Orders, revenue
        AsyncMock(fetchall=lambda: [(1, "Pizza", 10)]),  # Top items
        AsyncMock(fetchall=lambda: [(18, 5)])  # Peak hours
    ]
    
    result = await compute_kpis(mock_db, date="2025-08-20", range_type="daily")
    
    logger.info(f"Test compute_kpis_daily: {result}")
    assert result["total_orders"] == 10
    assert result["total_revenue"] == 200.0
    assert result["top_items"][0]["name"] == "Pizza"
    assert result["peak_hours"] == [18]
    mock_db.execute.assert_called()