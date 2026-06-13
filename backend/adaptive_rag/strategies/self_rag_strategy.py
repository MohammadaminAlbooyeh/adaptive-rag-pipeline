from backend.adaptive_rag.strategies.base_strategy import BaseStrategy


class SelfRAGStrategy(BaseStrategy):
    def name(self) -> str:
        return "self_rag"

    def description(self) -> str:
        return "Self-reflective RAG with retrieve-grade-decide loop"

    async def execute(self, query: str, **kwargs) -> dict:
        return {
            "strategy": self.name(),
            "query": query,
            "answer": "Self-RAG response",
            "sources": [],
        }
