from backend.adaptive_rag.router.query_router import QueryRouter


async def main():
    router = QueryRouter()
    result = router.route("What is the capital of France?")
    print(f"Query: {result['query']}")
    print(f"Strategy: {result['strategy']}")
    print(f"Confidence: {result['confidence']}")
