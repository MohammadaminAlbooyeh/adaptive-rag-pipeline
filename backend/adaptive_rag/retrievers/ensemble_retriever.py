from typing import List
from backend.adaptive_rag.retrievers.base_retriever import BaseRetriever


class EnsembleRetriever(BaseRetriever):
    def __init__(self, retrievers: List[BaseRetriever], weights: List[float] = None):
        self.retrievers = retrievers
        self.weights = weights or [1.0 / len(retrievers)] * len(retrievers)

    async def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        return []
