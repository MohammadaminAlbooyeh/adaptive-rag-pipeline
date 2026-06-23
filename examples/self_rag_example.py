import asyncio
import sys
from backend.llm.llm_factory import LLMFactory
from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever
from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader
from backend.adaptive_rag.graders.hallucination_grader import HallucinationGrader
from backend.adaptive_rag.strategies.self_rag_strategy import SelfRAGStrategy


async def main():
    try:
        llm = LLMFactory.create("openai")
        retriever = VectorRetriever(vector_store=None)
        relevance_grader = RelevanceGrader(llm=llm)
        hallucination_grader = HallucinationGrader(llm=llm)
        strategy = SelfRAGStrategy(
            retriever=retriever,
            llm=llm,
            relevance_grader=relevance_grader,
            hallucination_grader=hallucination_grader,
        )

        query = "Explain how self-reflective RAG improves answer quality"
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])

        print(f"Self-RAG query: {query}")
        result = await strategy.execute(query)
        print(f"\nStrategy: {result['strategy']}")
        print(f"Iterations: {result.get('iterations', 'N/A')}")
        print(f"Answer: {result['answer']}")
        print(f"\nSources ({len(result['sources'])}):")
        for s in result['sources']:
            print(f"  - {s['source']} (score: {s['score']})")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
