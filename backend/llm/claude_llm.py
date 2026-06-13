from langchain_anthropic import ChatAnthropic


class ClaudeLLM:
    def __init__(self, model: str = "claude-3-opus-20240229"):
        self.llm = ChatAnthropic(model=model, temperature=0)

    async def generate(self, prompt: str) -> str:
        response = await self.llm.ainvoke(prompt)
        return response.content
