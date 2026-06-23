class ClassificationChain:
    def __init__(self, llm, prompt):
        self.chain = prompt | llm

    async def classify(self, query: str) -> dict:
        result = await self.chain.ainvoke({"query": query})
        text = result.content if hasattr(result, "content") else str(result)
        return {"text": text}
