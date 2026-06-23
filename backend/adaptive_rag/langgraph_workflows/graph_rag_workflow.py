from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from backend.adaptive_rag.retrievers.graph_retriever import GraphRetriever
from backend.adaptive_rag.generator.answer_generator import AnswerGenerator
from backend.adaptive_rag.generator.context_builder import ContextBuilder
from backend.adaptive_rag.generator.response_formatter import ResponseFormatter


class GraphRAGState(TypedDict):
    query: str
    entities: list
    relations: list
    answer: str


class GraphRAGWorkflow:
    def __init__(self, llm, vector_store):
        self.llm = llm
        self.graph_retriever = GraphRetriever(vector_store)
        self.answer_generator = AnswerGenerator(llm)
        self.context_builder = ContextBuilder()
        self.response_formatter = ResponseFormatter()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(GraphRAGState)
        workflow.add_node("extract_entities", self._extract_entities)
        workflow.add_node("traverse_graph", self._traverse_graph)
        workflow.add_node("generate", self._generate)
        workflow.set_entry_point("extract_entities")
        workflow.add_edge("extract_entities", "traverse_graph")
        workflow.add_edge("traverse_graph", "generate")
        workflow.add_edge("generate", END)
        return workflow.compile()

    async def _extract_entities(self, state: GraphRAGState) -> Dict[str, Any]:
        query = state["query"]
        words = query.split()
        entities = []
        for w in words:
            cleaned = w.strip(".,!?;:()[]{}\"'")
            if len(cleaned) > 3 and (cleaned[0].isupper() or cleaned.isupper()):
                entities.append(cleaned)

        if not entities:
            entities = [w for w in words if len(w) > 3][:3]

        return {"entities": entities}

    async def _traverse_graph(self, state: GraphRAGState) -> Dict[str, Any]:
        entities = state.get("entities", [])
        relations = []

        for entity in entities:
            results = await self.graph_retriever.retrieve(entity, top_k=3)
            for doc in results:
                if isinstance(doc, dict):
                    relations.append(doc)
                else:
                    relations.append(
                        {
                            "content": getattr(doc, "page_content", str(doc)),
                            "source": "graph",
                        }
                    )

        return {"relations": relations}

    async def _generate(self, state: GraphRAGState) -> Dict[str, Any]:
        relations = state.get("relations", [])
        context = self.context_builder.build(relations)
        entities_str = ", ".join(state.get("entities", []))

        if context:
            prompt = f"Based on the knowledge graph context below, answer the query.\n\nEntities: {entities_str}\n\nContext:\n{context}\n\nQuery: {state['query']}\n\nAnswer:"
            answer = await self.llm.generate(prompt)
        else:
            answer = await self.answer_generator.generate(state["query"], context)

        return {"answer": answer}

    async def run(self, query: str) -> Dict[str, Any]:
        result = await self.workflow.ainvoke(
            {
                "query": query,
                "entities": [],
                "relations": [],
                "answer": "",
            }
        )
        formatted = self.response_formatter.format(
            answer=result.get("answer", ""),
            sources=[r.get("source", "graph") for r in result.get("relations", [])],
            metadata={"entities": result.get("entities", [])},
        )
        return formatted
