from backend.adaptive_rag.strategies.base_strategy import BaseStrategy


class DocumentRAGStrategy(BaseStrategy):
    def name(self) -> str:
        return "document_rag"

    def description(self) -> str:
        return "Retrieve relevant documents and generate answer"

    async def execute(self, query: str, **kwargs) -> dict:
        return {
            "strategy": self.name(),
            "query": query,
            "answer": "Document RAG response",
            "sources": [],
        }
