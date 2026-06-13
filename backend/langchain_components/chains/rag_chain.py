from langchain.chains import LLMChain


class RAGChain:
    def __init__(self, llm, prompt):
        self.chain = LLMChain(llm=llm, prompt=prompt)

    async def run(self, query: str, context: str) -> str:
        return await self.chain.arun(query=query, context=context)
