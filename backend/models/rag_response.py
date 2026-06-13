from pydantic import BaseModel
from typing import Optional


class RAGResponse(BaseModel):
    query: str
    strategy: str
    answer: str
    sources: list
    confidence: float
    latency: float
    grading: Optional[dict] = None
