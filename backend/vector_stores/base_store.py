from abc import ABC, abstractmethod
from typing import List


class BaseVectorStore(ABC):
    @abstractmethod
    async def add_documents(self, documents: List[dict]):
        pass

    @abstractmethod
    async def similarity_search(self, query_embedding: list, top_k: int = 5) -> List[dict]:
        pass
