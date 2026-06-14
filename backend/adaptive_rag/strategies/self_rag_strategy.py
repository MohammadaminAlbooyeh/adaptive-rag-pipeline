from backend.adaptive_rag.strategies.base_strategy import BaseStrategy


class SelfRAGStrategy(BaseStrategy):
    def __init__(self, retriever, llm, relevance_grader, hallucination_grader):
        self.retriever = retriever
        self.llm = llm
        self.relevance_grader = relevance_grader
        self.hallucination_grader = hallucination_grader
        self.max_iterations = 3

    def name(self) -> str:
        return "self_rag"

    def description(self) -> str:
        return "Self-reflective RAG with retrieve-grade-decide loop"

    async def execute(self, query: str, **kwargs) -> dict:
        try:
            current_query = query
            iteration = 0
            all_documents = []
            final_answer = None

            while iteration < self.max_iterations and final_answer is None:
                docs = await self.retriever.retrieve(current_query, top_k=5)
                all_documents.extend(docs)

                relevant_docs = []
                for doc in docs:
                    relevance = await self.relevance_grader.grade(doc["content"], current_query)
                    if relevance["is_relevant"]:
                        relevant_docs.append(doc)

                if relevant_docs:
                    context = "\n\n".join([d["content"] for d in relevant_docs])
                    answer = await self.llm.generate_with_context(current_query, context)

                    hallucination = await self.hallucination_grader.grade(answer, context)
                    if hallucination["is_grounded"]:
                        final_answer = answer
                        break
                    else:
                        current_query = f"{query} (previous answer was incorrect, try again differently)"

                iteration += 1

            if final_answer is None:
                final_answer = await self.llm.generate(f"Answer this question: {query}")

            sources = [
                {
                    "content": d.get("content", "")[:100],
                    "source": d.get("source", "Unknown"),
                    "score": d.get("relevance_score", 0)
                }
                for d in all_documents[:5]
            ]

            return {
                "strategy": self.name(),
                "query": query,
                "answer": final_answer,
                "sources": sources,
                "documents": all_documents,
                "iterations": iteration + 1,
            }
        except Exception as e:
            return {
                "strategy": self.name(),
                "query": query,
                "answer": f"Self-RAG failed: {str(e)}",
                "sources": [],
                "documents": [],
            }
