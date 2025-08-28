import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from db.connection import get_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup in-memory SQLite for integration tests
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override dependency for in-memory DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """FastAPI test client with in-memory DB."""
    with engine.connect() as conn:
        # Create schema
        with open("db/schema.sql", "r") as f:
            conn.execute(f.read())
        conn.commit()
    return TestClient(app)

@pytest.mark.asyncio
async def test_orchestrated_table_assignment(client):
    """Test orchestrated flow: Vision -> Orchestrator -> Order -> Analytics."""
    # Seed minimal data
    db = TestingSessionLocal()
    db.execute("INSERT INTO tables (table_number, capacity, status) VALUES (1, 4, 'available')")
    db.execute("INSERT INTO reservations (customer_name, reservation_time, table_id) VALUES ('Alice', '2025-08-20 18:00:00', 1)")
    db.commit()
    
    with patch("app.orchestrator.publish_event", new=AsyncMock()) as mock_publish:
        # Simulate vision event
        response = client.post("/api/vision/ingest", files={"file": ("table1.png", b"mock_image", "image/png")}, data={"table_id": 1})
        
        logger.info(f"Test orchestrated_table_assignment vision response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "detected_empty"
        
        # Check order creation via orchestrator
        orders = db.execute("SELECT * FROM orders WHERE table_id = 1").fetchall()
        logger.info(f"Test orchestrated_table_assignment orders: {orders}")
        assert len(orders) == 1
        
        # Check analytics update
        analytics = db.execute("SELECT * FROM analytics_daily WHERE date = '2025-08-20'").fetchall()
        logger.info(f"Test orchestrated_table_assignment analytics: {analytics}")
        assert len(analytics) == 1
        
        mock_publish.assert_called()
    
    db.close()