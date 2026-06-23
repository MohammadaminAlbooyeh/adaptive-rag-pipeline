class GradingChain:
    def __init__(self, llm, prompt):
        self.chain = prompt | llm

    async def grade(self, document: str, query: str) -> dict:
        result = await self.chain.ainvoke({"document": document, "query": query})
        text = result.content if hasattr(result, "content") else str(result)
        return {"text": text}
