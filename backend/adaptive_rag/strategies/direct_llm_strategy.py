from backend.adaptive_rag.strategies.base_strategy import BaseStrategy


class DirectLLMStrategy(BaseStrategy):
    def __init__(self, llm):
        self.llm = llm

    def name(self) -> str:
        return "direct_llm"

    def description(self) -> str:
        return "Answer directly using LLM knowledge without retrieval"

    async def execute(self, query: str, **kwargs) -> dict:
        try:
            answer = await self.llm.generate(
                f"Answer the following question:\n\n{query}"
            )
            return {
                "strategy": self.name(),
                "query": query,
                "answer": answer,
                "sources": [],
                "documents": [],
            }
        except Exception as e:
            return {
                "strategy": self.name(),
                "query": query,
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "documents": [],
            }
