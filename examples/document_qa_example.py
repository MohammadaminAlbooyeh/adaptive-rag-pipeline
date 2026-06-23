import asyncio
from backend.llm.llm_factory import LLMFactory
from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever
from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader
from backend.adaptive_rag.strategies.document_rag_strategy import DocumentRAGStrategy


async def main():
    llm = LLMFactory.create("openai")
    retriever = VectorRetriever(vector_store=None)
    grader = RelevanceGrader(llm=llm)
    strategy = DocumentRAGStrategy(retriever=retriever, llm=llm, grader=grader)

    query = "What is adaptive RAG?"
    result = await strategy.execute(query)
    print(f"Strategy: {result['strategy']}")
    print(f"Answer: {result['answer']}")


if __name__ == "__main__":
    asyncio.run(main())
