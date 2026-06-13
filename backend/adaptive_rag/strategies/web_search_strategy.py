from backend.adaptive_rag.strategies.base_strategy import BaseStrategy


class WebSearchStrategy(BaseStrategy):
    def name(self) -> str:
        return "web_search_rag"

    def description(self) -> str:
        return "Search the web and retrieve fresh information"

    async def execute(self, query: str, **kwargs) -> dict:
        return {
            "strategy": self.name(),
            "query": query,
            "answer": "Web search RAG response",
            "sources": [],
        }
