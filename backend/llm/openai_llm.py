from langchain_openai import ChatOpenAI


class OpenAILLM:
    def __init__(self, model: str = "gpt-4"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    async def generate(self, prompt: str) -> str:
        response = await self.llm.ainvoke(prompt)
        return response.content
