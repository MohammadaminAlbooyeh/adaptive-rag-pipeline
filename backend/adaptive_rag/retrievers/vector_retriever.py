from typing import List
from backend.adaptive_rag.retrievers.base_retriever import BaseRetriever


class VectorRetriever(BaseRetriever):
    def __init__(self, vector_store):
        self.vector_store = vector_store

    async def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        return []
