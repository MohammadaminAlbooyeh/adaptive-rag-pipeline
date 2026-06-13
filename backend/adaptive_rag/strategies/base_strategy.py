from abc import ABC, abstractmethod
from typing import Any


class BaseStrategy(ABC):
    @abstractmethod
    async def execute(self, query: str, **kwargs) -> Any:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass
