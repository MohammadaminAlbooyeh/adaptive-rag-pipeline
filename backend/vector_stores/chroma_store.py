from typing import List
from backend.vector_stores.base_store import BaseVectorStore


class ChromaStore(BaseVectorStore):
    def __init__(self, persist_directory: str = "./chromadb"):
        self.persist_directory = persist_directory

    async def add_documents(self, documents: List[dict]):
        pass

    async def similarity_search(self, query_embedding: list, top_k: int = 5) -> List[dict]:
        return []
