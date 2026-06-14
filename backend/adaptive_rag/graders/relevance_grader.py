class RelevanceGrader:
    def __init__(self, llm=None):
        self.llm = llm

    async def grade(self, document: str, query: str) -> dict:
        if self.llm:
            is_relevant = await self.llm.grade_relevance(document, query)
            return {
                "score": 1.0 if is_relevant else 0.0,
                "is_relevant": is_relevant,
                "explanation": "Graded by LLM",
            }

        score = self._compute_relevance_score(document, query)
        return {
            "score": score,
            "is_relevant": score > 0.5,
            "explanation": "Computed by keyword matching",
        }

    def _compute_relevance_score(self, document: str, query: str) -> float:
        query_words = set(query.lower().split())
        doc_words = set(document.lower().split())

        if not query_words:
            return 0.0

        overlap = len(query_words.intersection(doc_words))
        return min(overlap / len(query_words), 1.0)
