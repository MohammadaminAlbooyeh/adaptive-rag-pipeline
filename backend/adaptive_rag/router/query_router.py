from backend.adaptive_rag.router.query_classifier import QueryClassifier
from backend.adaptive_rag.router.strategy_selector import StrategySelector
from backend.adaptive_rag.router.confidence_scorer import ConfidenceScorer


class QueryRouter:
    def __init__(self):
        self.classifier = QueryClassifier()
        self.selector = StrategySelector()
        self.scorer = ConfidenceScorer()

    def route(self, query: str) -> dict:
        classification = self.classifier.classify(query)
        strategy = self.selector.select(classification)
        confidence = self.scorer.score(classification, strategy)
        return {
            "query": query,
            "classification": classification,
            "strategy": strategy,
            "confidence": confidence,
        }
