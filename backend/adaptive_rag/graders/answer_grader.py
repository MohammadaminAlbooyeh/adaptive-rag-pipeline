class AnswerGrader:
    def grade(self, answer: str, query: str) -> dict:
        return {
            "quality_score": 0.0,
            "answers_query": False,
            "explanation": "",
        }
