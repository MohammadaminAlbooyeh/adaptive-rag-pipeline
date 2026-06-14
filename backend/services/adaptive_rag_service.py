from backend.adaptive_rag.router.query_classifier import QueryClassifier
from backend.adaptive_rag.router.strategy_selector import StrategySelector
from backend.adaptive_rag.router.confidence_scorer import ConfidenceScorer


class AdaptiveRAGService:
    def __init__(self, strategies: dict = None):
        self.strategies = strategies or {}
        self.classifier = QueryClassifier()
        self.selector = StrategySelector()
        self.confidence_scorer = ConfidenceScorer()

    def register_strategy(self, name: str, strategy):
        self.strategies[name] = strategy

    async def process_query(self, query: str, **kwargs) -> dict:
        try:
            classification = self.classifier.classify(query)
            strategy_name = self.selector.select(classification)
            strategy = self.strategies.get(strategy_name)

            if not strategy:
                return {
                    "query": query,
                    "strategy": strategy_name,
                    "answer": f"Strategy '{strategy_name}' not implemented",
                    "sources": [],
                    "confidence": 0.0,
                }

            result = await strategy.execute(query, **kwargs)

            confidence = self.confidence_scorer.score(result)
            result["confidence"] = confidence
            result["classification"] = {
                "query_type": classification.query_type,
                "complexity": classification.complexity,
                "needs_docs": classification.needs_docs,
                "needs_web": classification.needs_web,
                "is_time_sensitive": classification.is_time_sensitive,
                "needs_graph": classification.needs_graph,
            }

            return result
        except Exception as e:
            return {
                "query": query,
                "strategy": "error",
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "confidence": 0.0,
            }
