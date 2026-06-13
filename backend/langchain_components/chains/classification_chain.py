from langchain.chains import LLMChain


class ClassificationChain:
    def __init__(self, llm, prompt):
        self.chain = LLMChain(llm=llm, prompt=prompt)

    async def classify(self, query: str) -> dict:
        return await self.chain.arun(query=query)
