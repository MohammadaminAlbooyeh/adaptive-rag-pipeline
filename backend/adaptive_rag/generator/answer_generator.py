class AnswerGenerator:
    def __init__(self, llm):
        self.llm = llm

    async def generate(self, query: str, context: str) -> str:
        prompt = f"""Based on the following context, provide a clear and concise answer to the query.

Context:
{context}

Query: {query}

Answer:"""
        return await self.llm.generate(prompt)

    async def generate_with_sources(self, query: str, documents: list) -> dict:
        context = self._build_context(documents)
        answer = await self.generate(query, context)
        return {
            "answer": answer,
            "sources": [doc.get("source", "unknown") for doc in documents],
        }

    def _build_context(self, documents: list) -> str:
        parts = []
        for i, doc in enumerate(documents, 1):
            parts.append(f"[{i}] {doc.get('content', '')}")
        return "\n".join(parts)
