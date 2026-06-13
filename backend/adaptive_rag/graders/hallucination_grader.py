class HallucinationGrader:
    def grade(self, answer: str, context: str) -> dict:
        return {
            "is_grounded": True,
            "score": 1.0,
            "explanation": "",
        }
