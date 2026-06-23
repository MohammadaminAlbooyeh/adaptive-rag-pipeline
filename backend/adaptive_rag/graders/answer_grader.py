class AnswerGrader:
    def __init__(self, llm=None):
        self.llm = llm

    async def grade(self, answer: str, context: str) -> dict:
        if self.llm:
            is_grounded = await self.llm.grade_answer(answer, context)
            return {
                "quality_score": 1.0 if is_grounded else 0.5,
                "answers_query": is_grounded,
                "explanation": "Graded by LLM for grounding in context",
            }

        score = self._compute_quality_score(answer)
        return {
            "quality_score": score,
            "answers_query": score > 0.5,
            "explanation": "Graded by heuristics (length, punctuation)",
        }

    def _compute_quality_score(self, answer: str) -> float:
        if not answer:
            return 0.0

        score = 0.0
        if len(answer) > 50:
            score += 0.3
        if len(answer) > 200:
            score += 0.2
        if any(char in answer for char in ".!?"):
            score += 0.3
        if any(
            word in answer.lower()
            for word in ["because", "therefore", "thus", "however"]
        ):
            score += 0.2

        return min(score, 1.0)
