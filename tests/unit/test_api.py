import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.api.schemas import QueryRequest


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset the global service variables in routes between tests."""
    import backend.api.routes as routes
    routes._rag_service = None
    routes._document_service = None
    routes._indexing_service = None
    routes._analytics_service = None
    routes._llm = None
    routes._vector_store = None


class TestAPIHealth:
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "adaptive-rag-pipeline"

    @pytest.mark.asyncio
    async def test_api_v1_health(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data


class TestAPIQuery:
    @pytest.mark.asyncio
    async def test_query_endpoint_success(self):
        mock_service = AsyncMock()
        mock_service.process_query = AsyncMock(
            return_value={
                "query": "What is Python?",
                "strategy": "document_rag",
                "answer": "Python is a programming language.",
                "sources": [{"content": "Python info", "source": "doc.pdf"}],
                "confidence": 0.85,
            }
        )

        with patch("backend.api.routes._initialize_services"), \
             patch("backend.api.routes._rag_service", mock_service), \
             patch("backend.api.routes._analytics_service", AsyncMock()):

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/query",
                    json={"text": "What is Python?", "top_k": 5},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "What is Python?"
        assert data["strategy"] == "document_rag"
        assert data["answer"] == "Python is a programming language."
        assert isinstance(data["confidence"], (int, float))
        assert isinstance(data["latency"], (int, float))

    @pytest.mark.asyncio
    async def test_query_endpoint_with_custom_strategy(self):
        mock_service = AsyncMock()
        mock_service.process_query = AsyncMock(
            return_value={
                "query": "What is Python?",
                "strategy": "web_search_rag",
                "answer": "Python is popular.",
                "sources": [{"content": "Web result", "source": "https://example.com"}],
                "confidence": 0.75,
            }
        )

        with patch("backend.api.routes._initialize_services"), \
             patch("backend.api.routes._rag_service", mock_service), \
             patch("backend.api.routes._analytics_service", AsyncMock()):

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/query",
                    json={"text": "What is Python?", "strategy": "web_search_rag"},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["strategy"] == "web_search_rag"

    @pytest.mark.asyncio
    async def test_query_endpoint_error(self):
        mock_service = AsyncMock()
        mock_service.process_query = AsyncMock(side_effect=Exception("Service error"))

        with patch("backend.api.routes._initialize_services"), \
             patch("backend.api.routes._rag_service", mock_service), \
             patch("backend.api.routes._analytics_service", AsyncMock()):

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/query",
                    json={"text": "What is Python?"},
                )

        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_query_endpoint_invalid_body(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/query", json={})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_query_endpoint_empty_text(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/query", json={"text": ""})

        assert response.status_code in (200, 422)


class TestAPIDocuments:
    @pytest.mark.asyncio
    async def test_list_documents(self):
        mock_doc_service = AsyncMock()
        mock_doc_service.list_documents = AsyncMock(
            return_value=[
                {"id": "1", "filename": "test.pdf", "uploaded_at": "2024-01-01", "size": 100, "status": "uploaded"}
            ]
        )

        with patch("backend.api.routes._initialize_services"), \
             patch("backend.api.routes._document_service", mock_doc_service):

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data

    @pytest.mark.asyncio
    async def test_list_documents_empty(self):
        mock_doc_service = AsyncMock()
        mock_doc_service.list_documents = AsyncMock(return_value=[])

        with patch("backend.api.routes._initialize_services"), \
             patch("backend.api.routes._document_service", mock_doc_service):

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert data["documents"] == []

    @pytest.mark.asyncio
    async def test_delete_document(self):
        mock_doc_service = AsyncMock()
        mock_doc_service.delete_document = AsyncMock(return_value=True)

        with patch("backend.api.routes._initialize_services"), \
             patch("backend.api.routes._document_service", mock_doc_service), \
             patch("backend.api.routes._indexing_service", AsyncMock()):

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete("/api/v1/documents/test-id")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"

    @pytest.mark.asyncio
    async def test_delete_document_not_found(self):
        mock_doc_service = AsyncMock()
        mock_doc_service.delete_document = AsyncMock(return_value=False)

        with patch("backend.api.routes._initialize_services"), \
             patch("backend.api.routes._document_service", mock_doc_service):

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete("/api/v1/documents/non-existent")

        assert response.status_code == 200


class TestAPIStrategies:
    @pytest.mark.asyncio
    async def test_list_strategies(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/strategies")

        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        names = [s["name"] for s in data["strategies"]]
        assert "direct_llm" in names
        assert "document_rag" in names
        assert "web_search_rag" in names
        assert "hybrid_rag" in names
        assert "graph_rag" in names
        assert "self_rag" in names

    @pytest.mark.asyncio
    async def test_strategies_have_descriptions(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/strategies")

        data = response.json()
        for s in data["strategies"]:
            assert "description" in s
            assert len(s["description"]) > 0


class TestAPIAnalytics:
    @pytest.mark.asyncio
    async def test_analytics_endpoint(self):
        mock_analytics = AsyncMock()
        mock_analytics.get_stats = AsyncMock(
            return_value={
                "total_queries": 10,
                "avg_latency": 0.5,
                "avg_confidence": 0.85,
                "success_rate": 0.9,
                "strategy_distribution": {"document_rag": 5, "direct_llm": 5},
                "top_queries": [],
            }
        )

        with patch("backend.api.routes._initialize_services"), \
             patch("backend.api.routes._analytics_service", mock_analytics):

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/analytics")

        assert response.status_code == 200
        data = response.json()
        assert "total_queries" in data
        assert "avg_latency" in data
        assert "strategy_distribution" in data
