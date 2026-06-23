class RAGChain:
    def __init__(self, llm, prompt):
        self.chain = prompt | llm

    async def run(self, query: str, context: str) -> str:
        result = await self.chain.ainvoke({"query": query, "context": context})
        return result.content if hasattr(result, "content") else str(result)
