from backend.utils.config import settings


class LLMFactory:
    @staticmethod
    def create(provider: str = None):
        provider = provider or "openai"
        if provider == "openai":
            from backend.llm.openai_llm import OpenAILLM
            return OpenAILLM()
        if provider == "claude":
            from backend.llm.claude_llm import ClaudeLLM
            return ClaudeLLM()
        if provider == "groq":
            from backend.llm.groq_llm import GroqLLM
            return GroqLLM()
        if provider == "local":
            from backend.llm.local_llm import LocalLLM
            return LocalLLM()
        raise ValueError(f"Unknown provider: {provider}")
