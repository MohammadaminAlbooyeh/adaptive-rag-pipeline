from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever
from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader
from backend.adaptive_rag.graders.query_rewriter import QueryRewriter
from backend.adaptive_rag.generator.answer_generator import AnswerGenerator
from backend.adaptive_rag.generator.context_builder import ContextBuilder


class SelfRAGState(TypedDict):
    query: str
    documents: list
    reflection: str
    answer: str
    iteration: int


class SelfRAGWorkflow:
    def __init__(self, llm, vector_store):
        self.llm = llm
        self.vector_retriever = VectorRetriever(vector_store)
        self.relevance_grader = RelevanceGrader(llm)
        self.query_rewriter = QueryRewriter()
        self.answer_generator = AnswerGenerator(llm)
        self.context_builder = ContextBuilder()
        self.max_iterations = 3
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(SelfRAGState)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("reflect", self._reflect)
        workflow.add_node("generate", self._generate)
        workflow.set_entry_point("retrieve")
        workflow.add_conditional_edges(
            "retrieve",
            self._decide,
            {"reflect": "reflect", "generate": "generate"},
        )
        workflow.add_edge("reflect", "generate")
        workflow.add_edge("generate", END)
        return workflow.compile()

    async def _retrieve(self, state: SelfRAGState) -> Dict[str, Any]:
        iteration = state.get("iteration", 0)
        if iteration >= self.max_iterations:
            return {"documents": state.get("documents", [])}

        query = state["query"]
        docs = await self.vector_retriever.retrieve(query, top_k=5)
        return {"documents": docs, "iteration": iteration + 1}

    async def _reflect(self, state: SelfRAGState) -> Dict[str, Any]:
        documents = state.get("documents", [])
        query = state["query"]
        reflection_notes = []

        for doc in documents:
            result = await self.relevance_grader.grade(doc.get("content", ""), query)
            if not result.get("is_relevant", False):
                reflection_notes.append(f"Document not relevant: {doc.get('content', '')[:100]}...")

        if reflection_notes:
            feedback = "; ".join(reflection_notes)
            rewritten = self.query_rewriter.rewrite(query, feedback)
            if rewritten and rewritten != query:
                return {"reflection": "; ".join(reflection_notes), "query": rewritten}
            return {"reflection": "; ".join(reflection_notes)}

        return {"reflection": "All documents are relevant."}

    async def _generate(self, state: SelfRAGState) -> Dict[str, Any]:
        documents = state.get("documents", [])
        context = self.context_builder.build(documents)
        answer = await self.answer_generator.generate(state["query"], context) if context else await self.llm.generate(f"Answer: {state['query']}")
        return {"answer": answer}

    def _decide(self, state: SelfRAGState) -> str:
        iteration = state.get("iteration", 0)
        if iteration >= self.max_iterations:
            return "generate"
        return "reflect"

    async def run(self, query: str) -> Dict[str, Any]:
        result = await self.workflow.ainvoke({
            "query": query,
            "documents": [],
            "reflection": "",
            "answer": "",
            "iteration": 0,
        })
        return result
