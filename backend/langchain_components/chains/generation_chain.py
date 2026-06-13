from langchain.chains import LLMChain


class GenerationChain:
    def __init__(self, llm, prompt):
        self.chain = LLMChain(llm=llm, prompt=prompt)

    async def generate(self, query: str, context: str) -> str:
        return await self.chain.arun(query=query, context=context)
