from backend.adaptive_rag.router.query_classifier import ClassificationResult


def _make_classification(
    query_type="factual",
    complexity="simple",
    needs_docs=True,
    needs_web=False,
    is_time_sensitive=False,
    needs_graph=False,
):
    return ClassificationResult(
        query_type=query_type,
        complexity=complexity,
        needs_docs=needs_docs,
        needs_web=needs_web,
        is_time_sensitive=is_time_sensitive,
        needs_graph=needs_graph,
    )


class TestStrategySelector:
    def test_select_direct_llm(self, strategy_selector):
        classification = _make_classification(
            needs_docs=False, needs_web=False, needs_graph=False
        )
        assert strategy_selector.select(classification) == "direct_llm"

    def test_select_document_rag(self, strategy_selector):
        classification = _make_classification(
            needs_docs=True, needs_web=False, needs_graph=False
        )
        assert strategy_selector.select(classification) == "document_rag"

    def test_select_web_search_rag(self, strategy_selector):
        classification = _make_classification(
            needs_docs=False, needs_web=True, needs_graph=False
        )
        assert strategy_selector.select(classification) == "web_search_rag"

    def test_select_hybrid_rag(self, strategy_selector):
        classification = _make_classification(
            needs_docs=True, needs_web=True, needs_graph=False
        )
        assert strategy_selector.select(classification) == "hybrid_rag"

    def test_select_graph_rag_only(self, strategy_selector):
        classification = _make_classification(
            needs_docs=False, needs_web=False, needs_graph=True
        )
        assert strategy_selector.select(classification) == "graph_rag"

    def test_select_graph_with_docs(self, strategy_selector):
        classification = _make_classification(
            needs_docs=True, needs_web=False, needs_graph=True
        )
        assert strategy_selector.select(classification) == "document_rag"

    def test_select_graph_with_web(self, strategy_selector):
        classification = _make_classification(
            needs_docs=False, needs_web=True, needs_graph=True
        )
        assert strategy_selector.select(classification) == "web_search_rag"

    def test_select_graph_with_docs_and_web(self, strategy_selector):
        classification = _make_classification(
            needs_docs=True, needs_web=True, needs_graph=True
        )
        assert strategy_selector.select(classification) == "hybrid_rag"

    def test_select_factual_query(self, strategy_selector, query_classifier):
        classification = query_classifier.classify("What is Python?")
        strategy = strategy_selector.select(classification)
        assert strategy in ["document_rag", "direct_llm"]

    def test_select_time_sensitive(self, strategy_selector, query_classifier):
        classification = query_classifier.classify("latest news today")
        strategy = strategy_selector.select(classification)
        assert strategy == "web_search_rag"

    def test_select_opinion_no_docs(self, strategy_selector):
        classification = _make_classification(
            query_type="opinion", needs_docs=False, needs_web=False, needs_graph=False
        )
        assert strategy_selector.select(classification) == "direct_llm"

    def test_select_all_flags_false(self, strategy_selector):
        classification = _make_classification(
            needs_docs=False, needs_web=False, needs_graph=False
        )
        assert strategy_selector.select(classification) == "direct_llm"

    def test_select_document_rag_docs_only(self, strategy_selector):
        classification = _make_classification(
            needs_docs=True, needs_web=False, needs_graph=False
        )
        assert strategy_selector.select(classification) == "document_rag"

    def test_select_web_only(self, strategy_selector):
        classification = _make_classification(
            needs_docs=False, needs_web=True, needs_graph=False
        )
        assert strategy_selector.select(classification) == "web_search_rag"

    def test_select_hybrid_docs_and_web(self, strategy_selector):
        classification = _make_classification(
            needs_docs=True, needs_web=True, needs_graph=False
        )
        assert strategy_selector.select(classification) == "hybrid_rag"
