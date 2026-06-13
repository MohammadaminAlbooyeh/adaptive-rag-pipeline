from backend.adaptive_rag.strategies.base_strategy import BaseStrategy


class GraphRAGStrategy(BaseStrategy):
    def name(self) -> str:
        return "graph_rag"

    def description(self) -> str:
        return "Use knowledge graph for entity-based retrieval"

    async def execute(self, query: str, **kwargs) -> dict:
        return {
            "strategy": self.name(),
            "query": query,
            "answer": "Graph RAG response",
            "sources": [],
        }
