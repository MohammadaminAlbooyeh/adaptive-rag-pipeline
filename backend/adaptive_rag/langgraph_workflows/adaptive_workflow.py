from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from backend.adaptive_rag.router.query_classifier import QueryClassifier
from backend.adaptive_rag.router.strategy_selector import StrategySelector
from backend.adaptive_rag.router.confidence_scorer import ConfidenceScorer
from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever
from backend.adaptive_rag.retrievers.web_retriever import WebRetriever
from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader
from backend.adaptive_rag.graders.hallucination_grader import HallucinationGrader
from backend.adaptive_rag.graders.answer_grader import AnswerGrader
from backend.adaptive_rag.graders.query_rewriter import QueryRewriter
from backend.adaptive_rag.generator.answer_generator import AnswerGenerator
from backend.adaptive_rag.generator.context_builder import ContextBuilder
from backend.adaptive_rag.generator.response_formatter import ResponseFormatter


class WorkflowState(TypedDict):
    query: str
    query_type: str
    strategy: str
    documents: list
    web_results: list
    answer: str
    grade: str
    answer_quality: str
    generation_count: int
    web_search_count: int


class AdaptiveWorkflow:
    def __init__(self, llm, vector_store, classifier=None, selector=None, scorer=None):
        self.llm = llm
        self.vector_store = vector_store
        self.classifier = classifier or QueryClassifier()
        self.selector = selector or StrategySelector()
        self.scorer = scorer or ConfidenceScorer()
        self.vector_retriever = VectorRetriever(vector_store)
        self.web_retriever = WebRetriever()
        self.relevance_grader = RelevanceGrader(llm)
        self.hallucination_grader = HallucinationGrader(llm)
        self.answer_grader = AnswerGrader(llm)
        self.query_rewriter = QueryRewriter()
        self.answer_generator = AnswerGenerator(llm)
        self.context_builder = ContextBuilder()
        self.response_formatter = ResponseFormatter()
        self.max_iterations = 3
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(WorkflowState)
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("route_query", self._route_query)
        workflow.add_node("retrieve_documents", self._retrieve_documents)
        workflow.add_node("grade_documents", self._grade_documents)
        workflow.add_node("generate_answer", self._generate_answer)
        workflow.add_node("grade_answer", self._grade_answer)
        workflow.add_node("rewrite_query", self._rewrite_query)
        workflow.add_node("web_search", self._web_search)

        workflow.set_entry_point("classify_query")
        workflow.add_conditional_edges(
            "classify_query",
            self._decide_route,
            {"simple": "route_query", "complex": "route_query"},
        )
        workflow.add_edge("route_query", "retrieve_documents")
        workflow.add_conditional_edges(
            "grade_documents",
            self._decide_grade,
            {"relevant": "generate_answer", "not_relevant": "rewrite_query"},
        )
        workflow.add_conditional_edges(
            "grade_answer",
            self._decide_answer_quality,
            {
                "good": END,
                "hallucination": "generate_answer",
                "not_useful": "web_search",
            },
        )
        workflow.add_edge("rewrite_query", "retrieve_documents")
        workflow.add_edge("web_search", "generate_answer")

        return workflow.compile()

    async def _classify_query(self, state: WorkflowState) -> Dict[str, Any]:
        classification = self.classifier.classify(state["query"])
        return {
            "query_type": classification.query_type,
            "strategy": self.selector.select(classification),
        }

    async def _route_query(self, state: WorkflowState) -> Dict[str, Any]:
        strategy = state.get("strategy", "document_rag")
        return {"strategy": strategy}

    async def _retrieve_documents(self, state: WorkflowState) -> Dict[str, Any]:
        generation_count = state.get("generation_count", 0)
        if generation_count >= self.max_iterations:
            return {"documents": state.get("documents", [])}

        docs = await self.vector_retriever.retrieve(state["query"], top_k=5)
        return {"documents": docs}

    async def _grade_documents(self, state: WorkflowState) -> Dict[str, Any]:
        documents = state.get("documents", [])
        if not documents:
            return {"grade": "not_relevant"}

        query = state["query"]
        relevance_results = []
        for doc in documents:
            result = await self.relevance_grader.grade(doc.get("content", ""), query)
            relevance_results.append(result)

        any_relevant = any(r.get("is_relevant", False) for r in relevance_results)
        return {"grade": "relevant" if any_relevant else "not_relevant"}

    async def _generate_answer(self, state: WorkflowState) -> Dict[str, Any]:
        query = state["query"]
        documents = state.get("documents", [])
        web_results = state.get("web_results", [])
        all_docs = documents + web_results
        context = self.context_builder.build(all_docs) if all_docs else ""

        if context:
            answer = await self.answer_generator.generate(query, context)
        else:
            answer = await self.llm.generate(f"Answer the following question: {query}")

        generation_count = state.get("generation_count", 0) + 1
        return {"answer": answer, "generation_count": generation_count}

    async def _grade_answer(self, state: WorkflowState) -> Dict[str, Any]:
        answer = state.get("answer", "")
        documents = state.get("documents", [])
        web_results = state.get("web_results", [])
        all_docs = documents + web_results
        context = self.context_builder.build(all_docs)

        hallucination_result = (
            await self.hallucination_grader.grade(answer, context)
            if context
            else {"is_grounded": True}
        )
        quality_result = (
            await self.answer_grader.grade(answer, context)
            if context
            else {"quality_score": 1.0, "answers_query": True}
        )

        if not hallucination_result.get("is_grounded", True):
            return {"answer_quality": "hallucination"}
        if not quality_result.get("answers_query", True):
            return {"answer_quality": "not_useful"}
        return {"answer_quality": "good"}

    async def _rewrite_query(self, state: WorkflowState) -> Dict[str, Any]:
        generation_count = state.get("generation_count", 0)
        if generation_count >= self.max_iterations:
            return {"query": state["query"]}

        feedback = "Documents were not relevant to the query."
        rewritten = await self.query_rewriter.rewrite(state["query"], feedback)
        rewritten = (
            rewritten
            if rewritten and rewritten != state["query"]
            else state["query"] + " (refined)"
        )
        return {"query": rewritten}

    async def _web_search(self, state: WorkflowState) -> Dict[str, Any]:
        web_search_count = state.get("web_search_count", 0)
        if web_search_count >= self.max_iterations:
            return {"web_results": state.get("web_results", [])}

        results = await self.web_retriever.retrieve(state["query"], top_k=3)
        return {"web_results": results, "web_search_count": web_search_count + 1}

    def _decide_route(self, state: WorkflowState) -> str:
        return "simple"

    def _decide_grade(self, state: WorkflowState) -> str:
        generation_count = state.get("generation_count", 0)
        if generation_count >= self.max_iterations:
            return "relevant"
        return state.get("grade", "not_relevant")

    def _decide_answer_quality(self, state: WorkflowState) -> str:
        return state.get("answer_quality", "good")

    async def run(self, query: str) -> Dict[str, Any]:
        result = await self.workflow.ainvoke(
            {
                "query": query,
                "query_type": "",
                "strategy": "",
                "documents": [],
                "web_results": [],
                "answer": "",
                "grade": "",
                "answer_quality": "",
                "generation_count": 0,
                "web_search_count": 0,
            }
        )
        formatted = self.response_formatter.format(
            answer=result.get("answer", ""),
            sources=[
                doc.get("source", "unknown") for doc in result.get("documents", [])
            ],
            metadata={
                "strategy": result.get("strategy", ""),
                "query_type": result.get("query_type", ""),
                "confidence": self.scorer.score(result),
            },
        )
        return formatted
