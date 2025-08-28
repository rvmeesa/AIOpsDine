import logging
import pickle
import os
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sqlalchemy.sql import text
from db.connection import get_db
from app.orchestrator import publish_event
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MODEL_PATH = "data/models/reco_model.pkl"

def load_model() -> LogisticRegression:
    """Load the pickled scikit-learn model."""
    if not os.path.exists(MODEL_PATH):
        raise ValueError("Model not found. Train first.")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info("Recommendation model loaded")
    return model

async def get_recommendations(order_id: int) -> List[Dict]:
    """Generate upsell suggestions for an order using the loaded model."""
    try:
        model = load_model()
        with next(get_db()) as db:
            # Fetch current order items
            current_items = db.execute(
                text("SELECT menu_id FROM order_items WHERE order_id = :order_id"),
                {"order_id": order_id}
            ).fetchall()
            current_menu_ids = [row.menu_id for row in current_items]

            # Fetch features: time/day, inventory, co-occurrence from history
            now = datetime.now()
            hour = now.hour
            day_of_week = now.weekday()

            # Simple feature engineering: average co-occurrence from history
            history = db.execute(
                text("""
                    SELECT oi1.menu_id as current, oi2.menu_id as suggested, COUNT(*) as co_count
                    FROM order_items oi1
                    JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.menu_id != oi2.menu_id
                    GROUP BY oi1.menu_id, oi2.menu_id
                """)
            ).fetchall()

            features = []
            for row in history:
                if row.current in current_menu_ids:
                    feature = [hour, day_of_week, row.co_count]
                    features.append((row.suggested, feature))

            if not features:
                return []

            # Predict uplift (probability of upsell acceptance)
            suggestions = []
            for suggested_id, feature in features:
                # Check inventory using correct menu id reference
                inventory = db.execute(
                    text("SELECT quantity FROM inventory WHERE ingredient = (SELECT name FROM menu WHERE id = :menu_id)"),
                    {"menu_id": suggested_id}
                ).fetchone()
                if inventory and inventory.quantity < 1:
                    continue  # Suppress low-stock

                uplift = model.predict_proba([feature])[0][1]
                suggestions.append({"item_id": suggested_id, "uplift": uplift})

            # Rank and return top 3
            suggestions.sort(key=lambda x: x["uplift"], reverse=True)
            top_suggestions = suggestions[:3]

            logger.info(f"Generated suggestions for order {order_id}: {top_suggestions}")

            # Publish event for orchestrator
            await publish_event("recommendation_generated", {"order_id": order_id, "suggestions": top_suggestions})

            return top_suggestions
    except Exception as e:
        logger.error(f"Recommendation generation failed: {str(e)}")
        raise