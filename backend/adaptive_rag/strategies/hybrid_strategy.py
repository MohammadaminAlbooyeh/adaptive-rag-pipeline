from backend.adaptive_rag.strategies.base_strategy import BaseStrategy


class HybridStrategy(BaseStrategy):
    def __init__(self, doc_retriever, web_retriever, llm):
        self.doc_retriever = doc_retriever
        self.web_retriever = web_retriever
        self.llm = llm

    def name(self) -> str:
        return "hybrid_rag"

    def description(self) -> str:
        return "Combine document and web search for comprehensive answers"

    async def execute(self, query: str, **kwargs) -> dict:
        try:
            doc_results = await self.doc_retriever.retrieve(query, top_k=3)
            web_results = await self.web_retriever.retrieve(query, top_k=2)

            all_results = doc_results + web_results

            if not all_results:
                return {
                    "strategy": self.name(),
                    "query": query,
                    "answer": "No relevant information found from documents or web.",
                    "sources": [],
                    "documents": [],
                }

            context = self._build_context(all_results)
            answer = await self.llm.generate_with_context(query, context)

            sources = [
                {
                    "content": result.get("content", "")[:100],
                    "source": result.get("source", "Unknown"),
                    "score": result.get("relevance_score", 0)
                }
                for result in all_results[:5]
            ]

            return {
                "strategy": self.name(),
                "query": query,
                "answer": answer,
                "sources": sources,
                "documents": all_results,
            }
        except Exception as e:
            return {
                "strategy": self.name(),
                "query": query,
                "answer": f"Hybrid search failed: {str(e)}",
                "sources": [],
                "documents": [],
            }

    def _build_context(self, results: list) -> str:
        parts = []
        for i, result in enumerate(results, 1):
            source = result.get("source", "Unknown")
            content = result.get("content", "")
            parts.append(f"[Source {i}: {source}]\n{content}")
        return "\n\n".join(parts)
