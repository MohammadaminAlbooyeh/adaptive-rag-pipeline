class LocalLLM:
    def __init__(self, model: str = "llama2"):
        self.model = model

    async def generate(self, prompt: str) -> str:
        return "Local LLM response"
