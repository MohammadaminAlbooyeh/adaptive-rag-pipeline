from backend.adaptive_rag.strategies.base_strategy import BaseStrategy


class GraphRAGStrategy(BaseStrategy):
    def __init__(self, graph_retriever, llm):
        self.graph_retriever = graph_retriever
        self.llm = llm

    def name(self) -> str:
        return "graph_rag"

    def description(self) -> str:
        return "Use knowledge graph for entity-based retrieval"

    async def execute(self, query: str, **kwargs) -> dict:
        try:
            graph_results = await self.graph_retriever.retrieve(query, top_k=kwargs.get("top_k", 5))

            if not graph_results:
                return {
                    "strategy": self.name(),
                    "query": query,
                    "answer": "No graph relationships found for this query.",
                    "sources": [],
                    "documents": [],
                }

            context = self._build_context(graph_results)
            answer = await self.llm.generate_with_context(query, context)

            sources = [
                {
                    "content": result.get("content", "")[:100],
                    "source": result.get("source", "Graph"),
                    "score": result.get("relevance_score", 0)
                }
                for result in graph_results
            ]

            return {
                "strategy": self.name(),
                "query": query,
                "answer": answer,
                "sources": sources,
                "documents": graph_results,
            }
        except Exception as e:
            return {
                "strategy": self.name(),
                "query": query,
                "answer": f"Graph retrieval failed: {str(e)}",
                "sources": [],
                "documents": [],
            }

    def _build_context(self, results: list) -> str:
        parts = []
        for result in results:
            parts.append(result.get("content", ""))
        return "\n".join(parts)
