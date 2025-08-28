import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.sql import text
from db.connection import get_db

# Configure logging for production readiness
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# In-memory event queue for MVP
event_queue = asyncio.Queue()

async def publish_event(event_type: str, payload: Dict):
    """Publish an event to the queue."""
    event = {"type": event_type, "payload": payload, "timestamp": datetime.utcnow().isoformat()}
    logger.info(f"Publishing event: {event_type}")
    await event_queue.put(event)

async def consume_events():
    """Process events from the queue."""
    while True:
        event = await event_queue.get()
        logger.info(f"Processing event: {event['type']}")
        try:
            if event["type"] == "table_status_update":
                await handle_table_status(event["payload"])
            elif event["type"] == "faq_query_processed":
                logger.info(f"FAQ query event: {event['payload']['query']} -> {event['payload']['response']}")
        except Exception as e:
            logger.error(f"Error processing event {event['type']}: {str(e)}")
        event_queue.task_done()

async def handle_table_status(payload: Dict):
    """Handle table status updates from Vision Agent."""
    table_id = payload.get("table_id")
    status = payload.get("status")
    if status == "detected_empty":
        await assign_table_to_reservation(table_id)

async def assign_table_to_reservation(table_id: int) -> Optional[Dict]:
    """Assign a table to a pending reservation or create an open order."""
    try:
        with next(get_db()) as db:
            # Check if table is available and has sufficient capacity
            table = db.execute(
                text("SELECT * FROM tables WHERE id = :table_id AND status = 'available'"),
                {"table_id": table_id}
            ).fetchone()
            if not table:
                logger.warning(f"Table {table_id} not available")
                return None

            # Find a pending reservation
            reservation = db.execute(
                text("SELECT * FROM reservations WHERE table_id IS NULL AND reservation_time <= :now ORDER BY reservation_time ASC"),
                {"now": datetime.utcnow()}
            ).fetchone()

            if reservation:
                # Assign table to reservation
                db.execute(
                    text("UPDATE reservations SET table_id = :table_id WHERE id = :reservation_id"),
                    {"table_id": table_id, "reservation_id": reservation.id}
                )
                # Create order
                order_id = db.execute(
                    text("INSERT INTO orders (table_id, reservation_id, status, created_at) VALUES (:table_id, :reservation_id, 'pending', :now)"),
                    {"table_id": table_id, "reservation_id": reservation.id, "now": datetime.utcnow()}
                ).lastrowid
                db.commit()
                logger.info(f"Assigned table {table_id} to reservation {reservation.id}, order {order_id}")
                return {"table_id": table_id, "order_id": order_id, "reservation_id": reservation.id}
            else:
                # No reservation; create walk-in order
                order_id = db.execute(
                    text("INSERT INTO orders (table_id, status, created_at) VALUES (:table_id, 'pending', :now)"),
                    {"table_id": table_id, "now": datetime.utcnow()}
                ).lastrowid
                db.execute(
                    text("UPDATE tables SET status = 'occupied' WHERE id = :table_id"),
                    {"table_id": table_id}
                )
                db.commit()
                logger.info(f"Assigned table {table_id} to walk-in, order {order_id}")
                return {"table_id": table_id, "order_id": order_id}
    except Exception as e:
        logger.error(f"Error assigning table {table_id}: {str(e)}")
        return None

async def start_orchestrator():
    """Start the orchestrator's event consumer."""
    logger.info("Starting orchestrator event consumer")
    asyncio.create_task(consume_events())

# Simulate Vision Agent event (for testing)
async def simulate_vision_event(table_id: int, status: str):
    await publish_event("table_status_update", {"table_id": table_id, "status": status})