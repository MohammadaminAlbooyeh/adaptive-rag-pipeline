from collections import defaultdict
from datetime import datetime


class AnalyticsService:
    def __init__(self):
        self.queries = []
        self.strategy_counts = defaultdict(int)
        self.latencies = []
        self.confidences = []

    async def log_query(
        self, query: str, strategy: str, latency: float, confidence: float = 0.0
    ):
        self.queries.append(
            {
                "query": query,
                "strategy": strategy,
                "latency": latency,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.strategy_counts[strategy] += 1
        self.latencies.append(latency)
        self.confidences.append(confidence)

    async def get_stats(self) -> dict:
        total = len(self.queries)
        avg_latency = (
            sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
        )
        avg_confidence = (
            sum(self.confidences) / len(self.confidences) if self.confidences else 0.0
        )

        successful = sum(1 for q in self.queries if q["confidence"] > 0.5)
        success_rate = successful / total if total > 0 else 0.0

        top_queries = self._get_top_queries()

        return {
            "total_queries": total,
            "avg_latency": round(avg_latency, 3),
            "avg_confidence": round(avg_confidence, 2),
            "success_rate": round(success_rate, 2),
            "strategy_distribution": dict(self.strategy_counts),
            "top_queries": top_queries,
        }

    def _get_top_queries(self) -> list:
        query_counts = defaultdict(int)
        for q in self.queries:
            query_counts[q["query"]] += 1

        return [
            {"query": q, "count": count}
            for q, count in sorted(
                query_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
        ]
