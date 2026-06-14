from backend.adaptive_rag.strategies.base_strategy import BaseStrategy
from typing import Optional


class DocumentRAGStrategy(BaseStrategy):
    def __init__(self, retriever, llm, grader):
        self.retriever = retriever
        self.llm = llm
        self.grader = grader

    def name(self) -> str:
        return "document_rag"

    def description(self) -> str:
        return "Retrieve relevant documents and generate answer"

    async def execute(self, query: str, **kwargs) -> dict:
        try:
            docs = await self.retriever.retrieve(query, top_k=kwargs.get("top_k", 5))
            if not docs:
                return {
                    "strategy": self.name(),
                    "query": query,
                    "answer": "No relevant documents found in the database.",
                    "sources": [],
                    "documents": [],
                }

            context = self._build_context(docs)
            answer = await self.llm.generate_with_context(query, context)

            filtered_sources = [doc for doc in docs if doc.get("relevance_score", 0) > 0.3]

            return {
                "strategy": self.name(),
                "query": query,
                "answer": answer,
                "sources": [{"content": doc["content"], "source": doc["source"], "score": doc.get("relevance_score")} for doc in filtered_sources],
                "documents": docs,
            }
        except Exception as e:
            return {
                "strategy": self.name(),
                "query": query,
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "documents": [],
            }

    def _build_context(self, documents: list) -> str:
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"Document {i}:\n{doc['content']}\nSource: {doc['source']}")
        return "\n\n".join(context_parts)
