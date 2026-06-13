from abc import ABC, abstractmethod
from typing import List


class BaseRetriever(ABC):
    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        pass
