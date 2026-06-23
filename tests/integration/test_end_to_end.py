import pytest
from unittest.mock import AsyncMock, MagicMock


class TestEndToEnd:
    @pytest.mark.asyncio
    async def test_query_classification_routes_to_correct_strategy(
        self, adaptive_rag_service
    ):
        result = await adaptive_rag_service.process_query("What is Python?")
        assert "strategy" in result
        assert result["strategy"] in ("document_rag", "direct_llm")
        assert "answer" in result
        assert len(result["answer"]) > 0

    @pytest.mark.asyncio
    async def test_time_sensitive_query_uses_web_search(self, adaptive_rag_service):
        result = await adaptive_rag_service.process_query("latest news today")
        assert result["strategy"] == "web_search_rag"

    @pytest.mark.asyncio
    async def test_service_returns_confidence_score(self, adaptive_rag_service):
        result = await adaptive_rag_service.process_query("What is Python?")
        assert "confidence" in result
        assert isinstance(result["confidence"], (int, float))
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_service_returns_classification_metadata(self, adaptive_rag_service):
        result = await adaptive_rag_service.process_query("What is Python?")
        assert "classification" in result
        assert result["classification"]["query_type"] == "factual"
        assert "complexity" in result["classification"]
        assert "needs_docs" in result["classification"]

    @pytest.mark.asyncio
    async def test_service_with_unimplemented_strategy(self):
        from backend.services.adaptive_rag_service import AdaptiveRAGService

        service = AdaptiveRAGService({})
        result = await service.process_query("What is Python?")
        assert result["strategy"] in ("document_rag", "direct_llm")
        assert "not implemented" in result["answer"]

    @pytest.mark.asyncio
    async def test_service_with_custom_strategies(self, mock_strategies):
        from backend.services.adaptive_rag_service import AdaptiveRAGService

        service = AdaptiveRAGService(mock_strategies)
        result = await service.process_query("What is Python?", top_k=3)
        assert "strategy" in result
        assert "answer" in result

    @pytest.mark.asyncio
    async def test_strategy_registration(self, mock_strategy):
        from backend.services.adaptive_rag_service import AdaptiveRAGService

        service = AdaptiveRAGService()
        service.register_strategy("custom", mock_strategy)
        assert "custom" in service.strategies
        assert service.strategies["custom"] is mock_strategy

    @pytest.mark.asyncio
    async def test_full_pipeline_with_mock_service(self):
        from backend.adaptive_rag.router.query_classifier import QueryClassifier
        from backend.adaptive_rag.router.strategy_selector import StrategySelector

        classifier = QueryClassifier()
        selector = StrategySelector()

        query = "Compare Python versus Java for web development"
        classification = classifier.classify(query)
        strategy_name = selector.select(classification)

        assert classification.query_type == "comparative"
        assert strategy_name in ("document_rag", "hybrid_rag", "graph_rag")

    @pytest.mark.asyncio
    async def test_service_error_returns_graceful_response(self):
        from backend.services.adaptive_rag_service import AdaptiveRAGService

        failing_strategy = AsyncMock()
        failing_strategy.execute = AsyncMock(side_effect=Exception("Strategy failed"))
        failing_strategy.name = MagicMock(return_value="failing")

        service = AdaptiveRAGService({"direct_llm": failing_strategy})
        result = await service.process_query("What is Python?")

        assert "answer" in result
        assert "error" not in result.get("strategy", "").lower()

    @pytest.mark.asyncio
    async def test_document_service_round_trip(self, mock_vector_store):
        from backend.services.document_service import DocumentService

        service = DocumentService(mock_vector_store)
        upload_result = await service.upload_document("test.txt", b"Python content")
        assert "id" in upload_result
        assert upload_result["filename"] == "test.txt"
        assert upload_result["status"] == "uploaded"

        doc_id = upload_result["id"]
        doc = await service.get_document(doc_id)
        assert doc is not None
        assert doc["id"] == doc_id

        delete_result = await service.delete_document(doc_id)
        assert delete_result is True

        deleted_doc = await service.get_document(doc_id)
        assert deleted_doc is None

    @pytest.mark.asyncio
    async def test_analytics_service_tracks_queries(self):
        from backend.services.analytics_service import AnalyticsService

        service = AnalyticsService()
        await service.log_query("What is Python?", "document_rag", 0.5, 0.85)
        await service.log_query("latest news", "web_search_rag", 0.3, 0.75)

        stats = await service.get_stats()
        assert stats["total_queries"] == 2
        assert stats["strategy_distribution"]["document_rag"] == 1
        assert stats["strategy_distribution"]["web_search_rag"] == 1
        assert stats["avg_latency"] == 0.4

    @pytest.mark.asyncio
    async def test_confidence_scorer_with_various_results(self):
        from backend.adaptive_rag.router.confidence_scorer import ConfidenceScorer

        scorer = ConfidenceScorer()

        score_no_sources = scorer.score(
            {
                "strategy": "direct_llm",
                "answer": "Python is a language.",
                "sources": [],
                "documents": [],
            }
        )
        assert score_no_sources == 0.95

        score_with_sources = scorer.score(
            {
                "strategy": "document_rag",
                "answer": "Python is a language.",
                "sources": [
                    {"content": "Python info", "source": "doc1.pdf"},
                    {"content": "More info", "source": "doc2.pdf"},
                ],
                "documents": [
                    {"content": "Python info"},
                    {"content": "More info"},
                ],
            }
        )
        assert score_with_sources > 0.85

    def test_confidence_levels(self):
        from backend.adaptive_rag.router.confidence_scorer import ConfidenceScorer

        scorer = ConfidenceScorer()
        assert scorer.get_confidence_level(0.95) == "high"
        assert scorer.get_confidence_level(0.80) == "medium"
        assert scorer.get_confidence_level(0.60) == "low"
        assert scorer.get_confidence_level(0.0) == "low"
        assert scorer.get_confidence_level(1.0) == "high"
