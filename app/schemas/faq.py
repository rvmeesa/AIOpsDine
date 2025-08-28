from pydantic import BaseModel

class FAQRequest(BaseModel):
    query: str

class FAQResponse(BaseModel):
    response: str