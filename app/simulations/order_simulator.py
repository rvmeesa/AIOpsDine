import aiohttp
import asyncio
import random
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def order_simulator():
    """
    Simulate orders during peak hours (12-2 PM, 6-8 PM) via /api/orders/create.
    Supports AIO SaaS: Automated order generation.
    """
    menu_items = [
        {"menu_id": 1, "quantity": 1},  # Margherita Pizza
        {"menu_id": 2, "quantity": 1},  # Vegan Burger
        {"menu_id": 6, "quantity": 2}   # Lemonade
    ]
    peak_hours = [(12, 14), (18, 20)]  # 12-2 PM, 6-8 PM

    async with aiohttp.ClientSession() as session:
        while True:
            now = datetime.now().time()
            is_peak = any(start <= now.hour < end for start, end in peak_hours)
            if is_peak:
                try:
                    payload = {
                        "table_id": random.randint(1, 5),
                        "items": random.sample(menu_items, k=random.randint(1, 3)),
                        "free_text": None
                    }
                    async with session.post(
                        "http://localhost:8000/api/orders/create",
                        json=payload
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"Created order: {data}")
                        else:
                            logger.error(f"Failed to create order: {response.status}")
                except Exception as e:
                    logger.error(f"Error creating order: {str(e)}")
            await asyncio.sleep(30)  # New order every 30 seconds during peak

if __name__ == "__main__":
    asyncio.run(order_simulator())