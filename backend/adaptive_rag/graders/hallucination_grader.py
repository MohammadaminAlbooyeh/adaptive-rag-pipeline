class HallucinationGrader:
    def __init__(self, llm=None):
        self.llm = llm

    async def grade(self, answer: str, context: str) -> dict:
        if self.llm:
            has_hallucination = await self.llm.detect_hallucination(answer, context)
            return {
                "is_grounded": not has_hallucination,
                "score": 0.0 if has_hallucination else 1.0,
                "explanation": "Checked by LLM for factual grounding",
            }

        score = self._compute_grounding_score(answer, context)
        return {
            "is_grounded": score > 0.5,
            "score": score,
            "explanation": "Heuristic check for grounding in context",
        }

    def _compute_grounding_score(self, answer: str, context: str) -> float:
        if not context:
            return 0.0

        answer_words = set(answer.lower().split())
        context_words = set(context.lower().split())

        if not answer_words:
            return 1.0

        overlap = len(answer_words.intersection(context_words))
        coverage = overlap / len(answer_words)

        return min(coverage, 1.0)
