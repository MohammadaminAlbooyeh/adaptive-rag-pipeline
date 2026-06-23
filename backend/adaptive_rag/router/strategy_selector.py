class StrategySelector:
    def select(self, classification) -> str:
        if (
            not classification.needs_docs
            and not classification.needs_web
            and not classification.needs_graph
        ):
            return "direct_llm"
        if classification.needs_docs and not classification.needs_web:
            return "document_rag"
        if classification.needs_web and not classification.needs_docs:
            return "web_search_rag"
        if classification.needs_docs and classification.needs_web:
            return "hybrid_rag"
        if classification.needs_graph:
            return "graph_rag"
        return "self_rag"
