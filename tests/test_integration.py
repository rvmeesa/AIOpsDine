import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.vision_agent.service import detect_table_status
from app.orchestrator import assign_table_to_reservation
from app.services.order_agent.service import create_order
from app.services.analytics_agent.service import compute_kpis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import logging

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_full_flow_integration():
    logger.info("Running test_full_flow_integration")
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as mock_db:
        mock_db.execute(text("CREATE TABLE vision_events (table_id INTEGER, event_type TEXT, timestamp DATETIME)"))
        mock_db.execute(text("CREATE TABLE tables (id INTEGER, status TEXT)"))
        mock_db.execute(text("CREATE TABLE orders (id INTEGER PRIMARY KEY, table_id INTEGER, status TEXT, created_at DATETIME)"))
        mock_db.execute(text("CREATE TABLE order_items (order_id INTEGER, menu_id INTEGER, quantity INTEGER)"))
        mock_db.execute(text("CREATE TABLE menu (id INTEGER, price REAL)"))
        mock_db.execute(text("INSERT INTO tables (id, status) VALUES (1, 'available')"))
        mock_db.execute(text("INSERT INTO menu (id, price) VALUES (1, 8.5), (2, 10.0)"))
        mock_db.commit()
        vision_result = detect_table_status("data\\sample_frames\\empty_table.png")
        assert vision_result["status"] == "detected_empty"
        orch_result = await assign_table_to_reservation(vision_result["table_id"])
        assert orch_result["order_id"] is not None
        items = [{"menu_id": 1, "quantity": 2}]
        await create_order(orch_result["table_id"], items, mock_db)
        kpis = await compute_kpis("2025-08-20", "daily", mock_db)
        assert kpis["total_orders"] > 0
        assert kpis["total_revenue"] > 0