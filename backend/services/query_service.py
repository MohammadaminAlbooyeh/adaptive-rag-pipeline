class QueryService:
    async def process(self, query: str, options: dict = None) -> dict:
        return {"query": query, "response": "Query response"}
