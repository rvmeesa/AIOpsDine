from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.vision import VisionResponse
from app.services.vision_agent.service import detect_table_status
import aiofiles
import os

router = APIRouter()

@router.post("/vision/ingest", response_model=VisionResponse)
async def ingest_image(file: UploadFile = File(...)):
    """FastAPI endpoint for image upload and detection."""
    try:
        if not file.filename.endswith(('.png', '.jpg')):
            raise HTTPException(400, "Invalid format")

        path = f"data/sample_frames/{file.filename}"
        async with aiofiles.open(path, 'wb') as f:
            await f.write(await file.read())

        result = await detect_table_status(path)  # Await async function
        return VisionResponse(**result)
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        # Clean up file
        if os.path.exists(path):
            os.remove(path)