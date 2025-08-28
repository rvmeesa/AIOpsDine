from pydantic import BaseModel
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    db_connected: bool
    timestamp: datetime
    message: str | None = None
