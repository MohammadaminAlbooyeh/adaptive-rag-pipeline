class GenerationChain:
    def __init__(self, llm, prompt):
        self.chain = prompt | llm

    async def generate(self, query: str, context: str) -> str:
        result = await self.chain.ainvoke({"query": query, "context": context})
        return result.content if hasattr(result, "content") else str(result)
