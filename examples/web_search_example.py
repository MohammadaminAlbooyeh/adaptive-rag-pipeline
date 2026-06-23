import asyncio
import sys
from backend.llm.llm_factory import LLMFactory
from backend.adaptive_rag.retrievers.web_retriever import WebRetriever
from backend.adaptive_rag.strategies.web_search_strategy import WebSearchStrategy


async def main():
    try:
        llm = LLMFactory.create("openai")
        web_retriever = WebRetriever()
        strategy = WebSearchStrategy(web_retriever=web_retriever, llm=llm)

        query = "Latest developments in AI 2026"
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])

        print(f"Searching web for: {query}")
        result = await strategy.execute(query)
        print(f"\nStrategy: {result['strategy']}")
        print(f"Answer: {result['answer']}")
        print(f"\nSources ({len(result['sources'])}):")
        for s in result['sources']:
            print(f"  - {s['source']} (score: {s['score']})")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
