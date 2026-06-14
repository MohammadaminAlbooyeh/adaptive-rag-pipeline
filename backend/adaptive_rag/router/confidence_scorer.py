class ConfidenceScorer:
    def score(self, result: dict) -> float:
        base_scores = {
            "direct_llm": 0.95,
            "document_rag": 0.85,
            "web_search_rag": 0.75,
            "hybrid_rag": 0.80,
            "graph_rag": 0.70,
            "self_rag": 0.90,
        }

        strategy = result.get("strategy", "unknown")
        base_score = base_scores.get(strategy, 0.5)

        num_sources = len(result.get("sources", []))
        source_bonus = min(num_sources * 0.05, 0.15)

        if "error" in result.get("answer", "").lower():
            base_score *= 0.5

        if result.get("documents"):
            doc_count = len(result.get("documents", []))
            doc_bonus = min(doc_count * 0.02, 0.1)
        else:
            doc_bonus = 0

        final_score = min(base_score + source_bonus + doc_bonus, 1.0)
        return round(final_score, 2)

    def get_confidence_level(self, score: float) -> str:
        if score >= 0.9:
            return "high"
        if score >= 0.7:
            return "medium"
        return "low"
