from backend.adaptive_rag.strategies.base_strategy import BaseStrategy
import asyncio


class WebSearchStrategy(BaseStrategy):
    def __init__(self, web_retriever, llm):
        self.web_retriever = web_retriever
        self.llm = llm

    def name(self) -> str:
        return "web_search_rag"

    def description(self) -> str:
        return "Search the web and retrieve fresh information"

    async def execute(self, query: str, **kwargs) -> dict:
        try:
            web_results = await self.web_retriever.retrieve(query, top_k=kwargs.get("top_k", 5))

            if not web_results:
                return {
                    "strategy": self.name(),
                    "query": query,
                    "answer": "No web search results found.",
                    "sources": [],
                    "documents": [],
                }

            context = self._build_context(web_results)
            answer = await self.llm.generate_with_context(query, context)

            sources = [
                {
                    "content": result.get("content", ""),
                    "source": result.get("source", "Web"),
                    "score": result.get("relevance_score", 0)
                }
                for result in web_results
            ]

            return {
                "strategy": self.name(),
                "query": query,
                "answer": answer,
                "sources": sources,
                "documents": web_results,
            }
        except Exception as e:
            return {
                "strategy": self.name(),
                "query": query,
                "answer": f"Web search failed: {str(e)}",
                "sources": [],
                "documents": [],
            }

    def _build_context(self, results: list) -> str:
        parts = []
        for i, result in enumerate(results, 1):
            source = result.get("source", "Unknown")
            content = result.get("content", "")
            parts.append(f"[{i}] {source}\n{content}")
        return "\n\n".join(parts)
