class QueryRewriter:
    def __init__(self, llm=None):
        self.llm = llm

    async def rewrite(self, query: str, feedback: str = "") -> str:
        if not self.llm:
            return query

        prompt = f"""Rewrite the following query to be more specific and searchable for a retrieval system.
Original query: {query}
{feedback}

Rewritten query:"""
        response = await self.llm.generate(prompt)
        return response.strip() or query
