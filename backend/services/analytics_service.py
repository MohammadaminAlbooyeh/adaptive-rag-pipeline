class AnalyticsService:
    async def log_query(self, query: str, strategy: str, latency: float):
        pass

    async def get_stats(self) -> dict:
        return {"total_queries": 0, "avg_latency": 0.0}
