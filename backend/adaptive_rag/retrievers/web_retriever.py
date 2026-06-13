from typing import List
from backend.adaptive_rag.retrievers.base_retriever import BaseRetriever


class WebRetriever(BaseRetriever):
    async def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        return []
