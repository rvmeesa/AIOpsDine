import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session
from app.services.faq_agent.service import answer_query
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_answer_query_menu():
    """Test FAQ Agent's answer_query for menu queries."""
    mock_db = AsyncMock(spec=Session)
    mock_db.execute.return_value.fetchall.return_value = [
        (1, "Vegan Burger", "Plant-based patty", 10.0, "main", 1, 1)
    ]
    
    with patch("app.services.faq_agent.service.ChatOpenAI") as mock_llm:
        mock_llm.return_value.invoke.return_value.content = "Vegan Burger is available."
        result = await answer_query(mock_db, "What vegan dishes do you have?")
        
        logger.info(f"Test answer_query_menu: {result}")
        assert "Vegan Burger" in result
        mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_answer_query_reservation():
    """Test FAQ Agent's answer_query for reservation queries."""
    mock_db = AsyncMock(spec=Session)
    mock_db.execute.return_value.fetchall.return_value = [
        (1, "Alice Johnson", "2025-08-20 18:00:00", 1)
    ]
    
    with patch("app.services.faq_agent.service.ChatOpenAI") as mock_llm:
        mock_llm.return_value.invoke.return_value.content = "Reservation for Alice found."
        result = await answer_query(mock_db, "Check reservation for Alice")
        
        logger.info(f"Test answer_query_reservation: {result}")
        assert "Alice" in result
        mock_db.execute.assert_called_once()