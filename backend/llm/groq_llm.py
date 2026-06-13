class GroqLLM:
    def __init__(self, model: str = "mixtral-8x7b-32768"):
        self.model = model

    async def generate(self, prompt: str) -> str:
        return "Groq response"
