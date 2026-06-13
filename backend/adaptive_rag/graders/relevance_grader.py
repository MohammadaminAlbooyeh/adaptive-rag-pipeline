class RelevanceGrader:
    def grade(self, document: str, query: str) -> dict:
        return {
            "score": 0.0,
            "is_relevant": False,
            "explanation": "",
        }
