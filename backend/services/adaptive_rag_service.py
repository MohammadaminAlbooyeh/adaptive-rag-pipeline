class AdaptiveRAGService:
    def __init__(self):
        self.strategies = {}

    def register_strategy(self, name: str, strategy):
        self.strategies[name] = strategy

    async def process_query(self, query: str) -> dict:
        return {"query": query, "strategy": "direct_llm", "answer": "Adaptive RAG response"}
