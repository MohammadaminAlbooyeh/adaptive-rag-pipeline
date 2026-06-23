from backend.adaptive_rag.router.query_classifier import QueryClassifier
from backend.adaptive_rag.router.strategy_selector import StrategySelector
from backend.adaptive_rag.router.confidence_scorer import ConfidenceScorer


class QueryService:
    def __init__(self):
        self.classifier = QueryClassifier()
        self.selector = StrategySelector()
        self.scorer = ConfidenceScorer()

    async def process(self, query: str, options: dict = None) -> dict:
        options = options or {}
        classification = self.classifier.classify(query)
        strategy_name = self.selector.select(classification)
        return {
            "query": query,
            "strategy": strategy_name,
            "classification": classification.model_dump(),
            "message": f"Query classified as {classification.query_type} with {classification.complexity} complexity",
        }
