import aiohttp
import asyncio
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def vision_simulator():
    """
    Simulate Vision Agent by posting images to /api/vision/ingest every 10 seconds.
    Supports AIO SaaS: Automated table status updates.
    """
    image_dir = Path("data/sample_frames")
    images = list(image_dir.glob("*.png"))  # Use sample images
    if not images:
        logger.error("No images found in data/sample_frames")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            for image_path in images:
                try:
                    async with session.post(
                        "http://localhost:8000/api/vision/ingest",
                        data={"file": open(image_path, "rb")}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"Posted {image_path}: {data}")
                        else:
                            logger.error(f"Failed to post {image_path}: {response.status}")
                except Exception as e:
                    logger.error(f"Error posting {image_path}: {str(e)}")
                await asyncio.sleep(10)  # Wait 10 seconds

if __name__ == "__main__":
    asyncio.run(vision_simulator())