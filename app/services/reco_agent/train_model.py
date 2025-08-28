import sys
import os
import importlib
importlib.invalidate_caches()  # Clear import cache
sys.path.insert(0, "C:\\r\\me\\projects\\ai-restaurant-manager")  # Absolute path to project root
print("Python Path:", sys.path)
from db.connection import get_db
import pickle
from sklearn.linear_model import LogisticRegression
from pandas import DataFrame
from sqlalchemy.sql import text
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MODEL_PATH = "data/models/reco_model.pkl"

def train_model():
    try:
        with next(get_db()) as db:
            # Fetch positive examples (co-occurring items)
            positive_data = db.execute(
                text("""
                    SELECT oi1.menu_id as current, oi2.menu_id as suggested, 1 as label, 
                           strftime('%H', o.created_at) as hour, strftime('%w', o.created_at) as day_of_week, 
                           COUNT(*) as co_count
                    FROM orders o
                    JOIN order_items oi1 ON o.id = oi1.order_id
                    JOIN order_items oi2 ON o.id = oi2.order_id AND oi1.menu_id != oi2.menu_id
                    GROUP BY oi1.menu_id, oi2.menu_id, hour, day_of_week
                """)
            ).fetchall()

            # Fetch negative examples (non-co-occurring items from different orders)
            negative_data = db.execute(
                text("""
                    SELECT oi1.menu_id as current, oi2.menu_id as suggested, 0 as label, 
                           strftime('%H', o1.created_at) as hour, strftime('%w', o1.created_at) as day_of_week, 
                           0 as co_count
                    FROM orders o1
                    JOIN order_items oi1 ON o1.id = oi1.order_id
                    JOIN orders o2 ON o1.id != o2.id
                    JOIN order_items oi2 ON o2.id = oi2.order_id
                    WHERE oi1.menu_id != oi2.menu_id
                    LIMIT 100 -- Limit to avoid excessive data
                """)
            ).fetchall()

            # Combine positive and negative examples
            data = positive_data + negative_data
            if not data:
                raise ValueError("No training data available")

            df = DataFrame(data, columns=["current", "suggested", "label", "hour", "day_of_week", "co_count"])
            X = df[["hour", "day_of_week", "co_count"]].astype(float)  # Convert to float for model
            y = df["label"]

            model = LogisticRegression()
            model.fit(X, y)

            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(model, f)

            logger.info("Recommendation model trained and saved")
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        raise

if __name__ == "__main__":
    train_model()