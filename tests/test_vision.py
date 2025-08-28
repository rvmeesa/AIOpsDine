import pytest
from unittest.mock import AsyncMock, patch
import numpy as np
from sqlalchemy.orm import Session
from app.services.vision_agent.service import detect_table_status
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_detect_table_status_empty():
    """Test Vision Agent's detect_table_status for empty table."""
    mock_db = AsyncMock(spec=Session)
    mock_image = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White image
    
    with patch("cv2.cvtColor") as mock_cvt, patch("cv2.threshold") as mock_thresh:
        mock_cvt.return_value = np.ones((100, 100), dtype=np.uint8) * 255
        mock_thresh.return_value = (None, np.ones((100, 100), dtype=np.uint8) * 255)
        result = await detect_table_status(mock_image, 1, mock_db)
        
        logger.info(f"Test detect_table_status_empty: {result}")
        assert result["status"] == "detected_empty"
        assert result["confidence"] > 0.7
        mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_detect_table_status_occupied():
    """Test Vision Agent's detect_table_status for occupied table."""
    mock_db = AsyncMock(spec=Session)
    mock_image = np.ones((100, 100, 3), dtype=np.uint8) * 50  # Dark image
    
    with patch("cv2.cvtColor") as mock_cvt, patch("cv2.threshold") as mock_thresh:
        mock_cvt.return_value = np.ones((100, 100), dtype=np.uint8) * 50
        mock_thresh.return_value = (None, np.zeros((100, 100), dtype=np.uint8))
        result = await detect_table_status(mock_image, 1, mock_db)
        
        logger.info(f"Test detect_table_status_occupied: {result}")
        assert result["status"] == "detected_occupied"
        assert result["confidence"] > 0.7
        mock_db.execute.assert_called_once()