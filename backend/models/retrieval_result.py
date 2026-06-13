from pydantic import BaseModel


class RetrievalResult(BaseModel):
    content: str
    score: float
    source: str
