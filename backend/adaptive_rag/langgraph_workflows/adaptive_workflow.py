from typing import Dict, Any
from langgraph.graph import StateGraph, END


class AdaptiveWorkflow:
    def __init__(self):
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(dict)
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
            {"good": END, "hallucination": "generate_answer", "not_useful": "web_search"},
        )
        workflow.add_edge("rewrite_query", "retrieve_documents")
        workflow.add_edge("web_search", "generate_answer")

        return workflow.compile()

    def _classify_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"query_type": "factual", "complexity": "simple"}

    def _route_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"strategy": "document_rag"}

    def _retrieve_documents(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"documents": []}

    def _grade_documents(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"grade": "relevant"}

    def _generate_answer(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"answer": "Generated answer"}

    def _grade_answer(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"answer_quality": "good"}

    def _rewrite_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"query": state.get("query", "")}

    def _web_search(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"web_results": []}

    def _decide_route(self, state: Dict[str, Any]) -> str:
        return "simple"

    def _decide_grade(self, state: Dict[str, Any]) -> str:
        return state.get("grade", "not_relevant")

    def _decide_answer_quality(self, state: Dict[str, Any]) -> str:
        return state.get("answer_quality", "good")

    async def run(self, query: str) -> Dict[str, Any]:
        return await self.workflow.ainvoke({"query": query})
