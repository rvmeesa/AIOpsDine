from pydantic import BaseModel

class VisionResponse(BaseModel):
    table_id: int
    status: str
    confidence: float