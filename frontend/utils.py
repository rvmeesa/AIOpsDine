import requests
import logging
from pydantic import BaseModel  # Ensure this is imported

logger = logging.getLogger(__name__)

class OrderItem(BaseModel):
    menu_id: int
    quantity: int
    
def send_faq_query(api_base: str, query: str) -> dict:
    """Send FAQ query to backend."""
    try:
        response = requests.post(f"{api_base}/faq/query", json={"query": query})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"FAQ API call failed: {str(e)}")
        raise

def upload_vision_image(api_base: str, file) -> dict:
    """Upload image for vision detection."""
    try:
        response = requests.post(f"{api_base}/vision/ingest", files={"file": file})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Vision API call failed: {str(e)}")
        raise
    
def create_order(api_base: str, table_id: int, items: list[OrderItem]) -> dict:
    logger.info(f"Calling create_order with table_id={table_id}, items={items}")
    # Convert OrderItem objects to dictionaries
    items_dict = [item.dict() for item in items]
    response = requests.post(
        f"{api_base}/orders/create",
        json={"table_id": table_id, "items": items_dict}  # Send as JSON
    )
    response.raise_for_status()
    return response.json()

def update_order_status(api_base: str, order_id: int, new_status: str) -> dict:
    """Update order status."""
    try:
        response = requests.put(f"{api_base}/orders/update", json={"order_id": order_id, "new_status": new_status})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Order update API call failed: {str(e)}")
        raise

def get_recommendations(api_base: str, order_id: int) -> dict:
    """Fetch recommendations for an order."""
    try:
        response = requests.post(f"{api_base}/reco/suggest", json={"order_id": order_id})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Recommendations API call failed: {str(e)}")
        raise

def get_analytics(api_base: str, date: str, range_type: str) -> dict:
    """Fetch analytics KPIs."""
    try:
        response = requests.get(f"{api_base}/analytics/summary", params={"date": date, "range": range_type})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Analytics API call failed: {str(e)}")
        raise