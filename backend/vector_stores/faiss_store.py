from typing import List
from backend.vector_stores.base_store import BaseVectorStore


class FAISSStore(BaseVectorStore):
    async def add_documents(self, documents: List[dict]):
        pass

    async def similarity_search(self, query_embedding: list, top_k: int = 5) -> List[dict]:
        return []
