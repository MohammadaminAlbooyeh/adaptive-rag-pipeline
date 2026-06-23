from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever
from backend.adaptive_rag.retrievers.web_retriever import WebRetriever
from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader
from backend.adaptive_rag.generator.answer_generator import AnswerGenerator
from backend.adaptive_rag.generator.context_builder import ContextBuilder


class CorrectiveRAGState(TypedDict):
    query: str
    documents: list
    grade: str
    corrected_docs: list
    answer: str


class CorrectiveRAGWorkflow:
    def __init__(self, llm, vector_store):
        self.llm = llm
        self.vector_retriever = VectorRetriever(vector_store)
        self.web_retriever = WebRetriever()
        self.relevance_grader = RelevanceGrader(llm)
        self.answer_generator = AnswerGenerator(llm)
        self.context_builder = ContextBuilder()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(CorrectiveRAGState)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("grade", self._grade)
        workflow.add_node("correct", self._correct)
        workflow.add_node("generate", self._generate)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "grade")
        workflow.add_conditional_edges(
            "grade",
            self._decide,
            {"correct": "correct", "generate": "generate"},
        )
        workflow.add_edge("correct", "generate")
        workflow.add_edge("generate", END)
        return workflow.compile()

    async def _retrieve(self, state: CorrectiveRAGState) -> Dict[str, Any]:
        docs = await self.vector_retriever.retrieve(state["query"], top_k=5)
        return {"documents": docs}

    async def _grade(self, state: CorrectiveRAGState) -> Dict[str, Any]:
        documents = state.get("documents", [])
        if not documents:
            return {"grade": "correct"}

        query = state["query"]
        relevance_scores = []
        for doc in documents:
            result = await self.relevance_grader.grade(doc.get("content", ""), query)
            relevance_scores.append(result.get("score", 0.0))

        avg_score = (
            sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        )
        return {"grade": "correct" if avg_score < 0.5 else "generate"}

    async def _correct(self, state: CorrectiveRAGState) -> Dict[str, Any]:
        web_results = await self.web_retriever.retrieve(state["query"], top_k=3)
        existing_docs = state.get("documents", [])
        source_urls = {d.get("source") for d in existing_docs if d.get("source")}
        new_docs = [d for d in web_results if d.get("source") not in source_urls]
        corrected_docs = existing_docs + new_docs
        return {"corrected_docs": corrected_docs}

    async def _generate(self, state: CorrectiveRAGState) -> Dict[str, Any]:
        corrected_docs = state.get("corrected_docs", [])
        documents = state.get("documents", [])
        all_docs = corrected_docs if corrected_docs else documents
        context = self.context_builder.build(all_docs)
        answer = (
            await self.answer_generator.generate(state["query"], context)
            if context
            else await self.llm.generate(f"Answer: {state['query']}")
        )
        return {"answer": answer}

    def _decide(self, state: CorrectiveRAGState) -> str:
        return state.get("grade", "generate")

    async def run(self, query: str) -> Dict[str, Any]:
        result = await self.workflow.ainvoke(
            {
                "query": query,
                "documents": [],
                "grade": "",
                "corrected_docs": [],
                "answer": "",
            }
        )
        return result
