import asyncio
import sys
from backend.llm.llm_factory import LLMFactory
from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever
from backend.adaptive_rag.retrievers.web_retriever import WebRetriever
from backend.adaptive_rag.strategies.hybrid_strategy import HybridStrategy


async def main():
    try:
        llm = LLMFactory.create("openai")
        doc_retriever = VectorRetriever(vector_store=None)
        web_retriever = WebRetriever()
        strategy = HybridStrategy(
            doc_retriever=doc_retriever,
            web_retriever=web_retriever,
            llm=llm,
        )

        query = "What is the latest research on retrieval augmented generation?"
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])

        print(f"Hybrid search for: {query}")
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
