from backend.adaptive_rag.strategies.base_strategy import BaseStrategy


class HybridStrategy(BaseStrategy):
    def name(self) -> str:
        return "hybrid_rag"

    def description(self) -> str:
        return "Combine multiple sources for comprehensive answers"

    async def execute(self, query: str, **kwargs) -> dict:
        return {
            "strategy": self.name(),
            "query": query,
            "answer": "Hybrid RAG response",
            "sources": [],
        }
