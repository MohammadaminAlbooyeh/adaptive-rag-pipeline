import pytest
from unittest.mock import MagicMock


class TestQueryRouter:
    @pytest.fixture
    def router(self):
        from backend.adaptive_rag.router.query_router import QueryRouter

        r = QueryRouter()
        r.scorer = MagicMock()
        r.scorer.score.return_value = 0.85
        return r

    def test_route_returns_dict(self, router):
        result = router.route("What is Python?")
        assert isinstance(result, dict)

    def test_route_contains_query(self, router):
        result = router.route("What is Python?")
        assert result["query"] == "What is Python?"

    def test_route_contains_classification(self, router):
        result = router.route("What is Python?")
        assert "classification" in result
        assert result["classification"].query_type == "factual"
        assert result["classification"].complexity == "simple"

    def test_route_contains_strategy(self, router):
        result = router.route("What is Python?")
        assert "strategy" in result
        assert isinstance(result["strategy"], str)

    def test_route_contains_confidence(self, router):
        result = router.route("What is Python?")
        assert "confidence" in result
        assert result["confidence"] == 0.85

    def test_route_simple_query_strategy(self, router):
        result = router.route("What is Python?")
        assert result["strategy"] in ("document_rag", "direct_llm")

    def test_route_time_sensitive_returns_web_search(self, router):
        router.scorer.score.return_value = 0.75
        result = router.route("latest news today")
        assert result["strategy"] == "web_search_rag"
        assert result["classification"].is_time_sensitive is True
        assert result["classification"].needs_web is True

    def test_route_comparative_query(self, router):
        result = router.route("Compare Python versus Java")
        assert result["classification"].query_type == "comparative"

    def test_route_procedural_query(self, router):
        result = router.route("How to install Python?")
        assert result["classification"].query_type == "procedural"

    def test_route_exploratory_query(self, router):
        result = router.route("Describe the theory of relativity")
        assert result["classification"].query_type == "exploratory"

    def test_route_opinion_query(self, router):
        result = router.route("What is the best programming language?")
        assert result["classification"].query_type == "opinion"

    def test_route_graph_query(self, router):
        router.scorer.score.return_value = 0.70
        result = router.route("What are the relationships between entities?")
        assert result["classification"].needs_graph is True

    def test_route_empty_query(self, router):
        router.scorer.score.return_value = 0.5
        result = router.route("")
        assert result["query"] == ""
        assert "classification" in result
        assert "strategy" in result

    def test_route_confidence_in_range(self, router):
        result = router.route("What is Python?")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_route_multiple_calls_have_different_strategies(self, router):
        router.scorer.score.side_effect = [0.85, 0.75]
        r1 = router.route("What is Python?")
        r2 = router.route("latest news")
        assert r1["strategy"] != r2["strategy"]

    def test_route_integrates_classifier_and_selector(self, router):
        router.scorer.score.return_value = 0.8
        result = router.route("Compare Python versus Java for data science")
        assert result["classification"].query_type == "comparative"
        assert result["classification"].complexity in ("simple", "moderate")
        assert "strategy" in result
