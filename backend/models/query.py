from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    text: str
    strategy: Optional[str] = None
    top_k: int = 5


class QueryResponse(BaseModel):
    query: str
    strategy: str
    answer: str
    sources: list
    confidence: float
    latency: float
