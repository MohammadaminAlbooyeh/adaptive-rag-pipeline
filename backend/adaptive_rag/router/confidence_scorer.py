class ConfidenceScorer:
    def score(self, classification, strategy: str) -> dict:
        base_confidence = {
            "direct_llm": 0.95,
            "document_rag": 0.85,
            "web_search_rag": 0.75,
            "hybrid_rag": 0.80,
            "graph_rag": 0.70,
            "self_rag": 0.90,
        }
        score = base_confidence.get(strategy, 0.5)
        return {
            "score": score,
            "level": self._level(score),
            "requires_retry": score < 0.6,
        }

    def _level(self, score: float) -> str:
        if score >= 0.9:
            return "high"
        if score >= 0.7:
            return "medium"
        return "low"
