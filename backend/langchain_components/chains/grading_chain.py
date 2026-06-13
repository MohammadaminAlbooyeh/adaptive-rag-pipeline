from langchain.chains import LLMChain


class GradingChain:
    def __init__(self, llm, prompt):
        self.chain = LLMChain(llm=llm, prompt=prompt)

    async def grade(self, document: str, query: str) -> dict:
        return await self.chain.arun(document=document, query=query)
