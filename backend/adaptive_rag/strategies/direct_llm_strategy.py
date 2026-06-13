from backend.adaptive_rag.strategies.base_strategy import BaseStrategy


class DirectLLMStrategy(BaseStrategy):
    def name(self) -> str:
        return "direct_llm"

    def description(self) -> str:
        return "Answer directly using LLM knowledge without retrieval"

    async def execute(self, query: str, **kwargs) -> dict:
        return {
            "strategy": self.name(),
            "query": query,
            "answer": "Direct LLM response",
            "sources": [],
        }
