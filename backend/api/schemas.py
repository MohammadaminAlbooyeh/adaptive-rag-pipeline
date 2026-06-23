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


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    status: str


class AnalyticsResponse(BaseModel):
    total_queries: int
    avg_latency: float
    strategy_distribution: dict
