import cv2
import asyncio
from datetime import datetime
from sqlalchemy.sql import text
from db.connection import get_db
from app.orchestrator import publish_event
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def detect_table_status(image_path: str) -> dict:
    """Detect table status using OpenCV ROI logic."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Image not loaded")

        height, width = img.shape[:2]
        roi = img[int(height*0.25):int(height*0.75), int(width*0.25):int(width*0.75)]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        brightness = gray.mean()

        threshold = 150
        status = "detected_empty" if brightness > threshold else "detected_occupied"
        confidence = min(1.0, abs(brightness - threshold) / 255)

        # Store in DB
        with next(get_db()) as db:
            db.execute(
                text("INSERT INTO vision_events (table_id, event_type, timestamp) VALUES (:table_id, :status, :ts)"),
                {"table_id": 1, "status": status, "ts": datetime.utcnow()}  # Assume table_id=1 for MVP
            )
            db.commit()

        # Publish event (await the async call)
        await publish_event("table_status_update", {"table_id": 1, "status": status})

        logger.info(f"Detected {status} with confidence {confidence}")
        return {"table_id": 1, "status": status, "confidence": confidence}  # Added table_id
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        raise