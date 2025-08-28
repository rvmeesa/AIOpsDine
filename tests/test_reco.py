import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session
from app.services.reco_agent.service import generate_suggestion
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_suggest_items():
    """Test Recommendation Agent's suggest_items."""
    mock_db = AsyncMock(spec=Session)
    mock_db.execute.side_effect = [
        AsyncMock(fetchall=lambda: [(1, 2)]),  # Order items
        AsyncMock(fetchall=lambda: [(1, 100), (2, 50)]),  # Inventory
        AsyncMock(fetchall=lambda: [(1, 10), (2, 5)]),  # Popularity
        AsyncMock(fetchall=lambda: [(2, "Lemonade", 3.5)])  # Menu
    ]
    
    with patch("app.services.reco_agent.service.model") as mock_model:
        mock_model.predict_proba.return_value = [[0.2, 0.8]]
        result = await generate_suggestion(mock_db, order_id=1)
        
        logger.info(f"Test suggest_items: {result}")
        assert len(result) > 0
        assert result[0]["item_id"] == 2
        assert result[0]["name"] == "Lemonade"
        mock_db.execute.assert_called()