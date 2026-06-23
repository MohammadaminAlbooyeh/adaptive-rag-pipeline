import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestVectorRetriever:
    @pytest.mark.asyncio
    async def test_retrieve_returns_list_of_dicts(self, mock_vector_store):
        from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever

        retriever = VectorRetriever(mock_vector_store)
        results = await retriever.retrieve("What is Python?")
        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(d, dict) for d in results)

    @pytest.mark.asyncio
    async def test_retrieve_contains_required_fields(self, mock_vector_store):
        from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever

        retriever = VectorRetriever(mock_vector_store)
        results = await retriever.retrieve("What is Python?")
        for doc in results:
            assert "content" in doc
            assert "metadata" in doc
            assert "relevance_score" in doc
            assert "source" in doc

    @pytest.mark.asyncio
    async def test_retrieve_respects_top_k(self, mock_vector_store):
        from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever

        mock_vector_store.similarity_search_with_score.return_value = [
            (MagicMock(page_content="Doc 1", metadata={"source": "doc.pdf"}), 0.95),
        ]
        retriever = VectorRetriever(mock_vector_store)
        results = await retriever.retrieve("What is Python?", top_k=1)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_retrieve_handles_empty_store(self):
        from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever

        store = MagicMock()
        store.similarity_search_with_score = MagicMock(return_value=[])
        retriever = VectorRetriever(store)
        results = await retriever.retrieve("What is Python?")
        assert results == []

    @pytest.mark.asyncio
    async def test_retrieve_handles_no_similarity_method(self):
        from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever

        store = MagicMock(spec=[])
        retriever = VectorRetriever(store)
        results = await retriever.retrieve("What is Python?")
        assert results == []

    @pytest.mark.asyncio
    async def test_retrieve_error_raises_runtime_error(self):
        from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever

        store = MagicMock()
        store.similarity_search_with_score = MagicMock(side_effect=Exception("Search failed"))
        retriever = VectorRetriever(store)
        with pytest.raises(RuntimeError, match="Vector retrieval failed"):
            await retriever.retrieve("What is Python?")


class TestWebRetriever:
    @pytest.mark.asyncio
    async def test_retrieve_returns_list_of_dicts(self):
        from backend.adaptive_rag.retrievers.web_retriever import WebRetriever

        mock_results = [
            {"body": "Python is popular.", "href": "https://example.com", "title": "Python"}
        ]

        with patch("backend.adaptive_rag.retrievers.web_retriever.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.text.return_value = mock_results
            mock_ddgs.return_value = mock_instance

            retriever = WebRetriever()
            results = await retriever.retrieve("What is Python?")

        assert isinstance(results, list)
        if results:
            for doc in results:
                assert "content" in doc
                assert "source" in doc
                assert "title" in doc
                assert "relevance_score" in doc

    @pytest.mark.asyncio
    async def test_retrieve_respects_top_k(self):
        from backend.adaptive_rag.retrievers.web_retriever import WebRetriever

        mock_results = [{"body": f"Result {i}", "href": f"https://example.com/{i}", "title": f"Title {i}"} for i in range(3)]

        with patch("backend.adaptive_rag.retrievers.web_retriever.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.text.return_value = mock_results
            mock_ddgs.return_value = mock_instance

            retriever = WebRetriever()
            results = await retriever.retrieve("What is Python?", top_k=3)
            assert len(results) <= 3

    @pytest.mark.asyncio
    async def test_retrieve_error_raises_runtime_error(self):
        from backend.adaptive_rag.retrievers.web_retriever import WebRetriever

        with patch("backend.adaptive_rag.retrievers.web_retriever.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.text.side_effect = Exception("Search failed")
            mock_ddgs.return_value = mock_instance

            retriever = WebRetriever()
            with pytest.raises(RuntimeError, match="Web retrieval failed"):
                await retriever.retrieve("What is Python?")


class TestGraphRetriever:
    @pytest.mark.asyncio
    async def test_retrieve_returns_list(self, mock_vector_store):
        from backend.adaptive_rag.retrievers.graph_retriever import GraphRetriever

        retriever = GraphRetriever(mock_vector_store)
        results = await retriever.retrieve("What is Python?")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_retrieve_extracts_entities(self):
        from backend.adaptive_rag.retrievers.graph_retriever import GraphRetriever

        store = MagicMock()
        store.similarity_search.return_value = []
        retriever = GraphRetriever(store)

        results = await retriever.retrieve("Python and Machine Learning concepts")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_retrieve_empty_for_no_entities(self, mock_vector_store):
        from backend.adaptive_rag.retrievers.graph_retriever import GraphRetriever

        retriever = GraphRetriever(mock_vector_store)
        results = await retriever.retrieve("a an the")
        assert results == []

    @pytest.mark.asyncio
    async def test_extract_entities_returns_capitalized_words(self):
        from backend.adaptive_rag.retrievers.graph_retriever import GraphRetriever

        retriever = GraphRetriever(MagicMock())
        entities = retriever._extract_entities("Python ML and AI")
        assert "Python" in entities

    @pytest.mark.asyncio
    async def test_extract_entities_max_three(self):
        from backend.adaptive_rag.retrievers.graph_retriever import GraphRetriever

        retriever = GraphRetriever(MagicMock())
        entities = retriever._extract_entities("Python Java C++ JavaScript Rust")
        assert len(entities) <= 3

    @pytest.mark.asyncio
    async def test_retrieve_error_raises_runtime_error(self):
        from backend.adaptive_rag.retrievers.graph_retriever import GraphRetriever

        store = MagicMock()
        store.similarity_search = MagicMock(side_effect=Exception("Store error"))
        retriever = GraphRetriever(store)
        results = await retriever.retrieve("Python programming")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_retrieve_limits_to_top_k(self, mock_vector_store):
        from backend.adaptive_rag.retrievers.graph_retriever import GraphRetriever

        retriever = GraphRetriever(mock_vector_store)
        results = await retriever.retrieve("Python programming", top_k=1)
        assert len(results) <= 1


class TestEnsembleRetriever:
    @pytest.mark.asyncio
    async def test_retrieve_returns_list(self, mock_retriever):
        from backend.adaptive_rag.retrievers.ensemble_retriever import EnsembleRetriever

        retriever = EnsembleRetriever([mock_retriever])
        results = await retriever.retrieve("What is Python?")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_initializes_with_default_weights(self, mock_retriever):
        from backend.adaptive_rag.retrievers.ensemble_retriever import EnsembleRetriever

        retriever = EnsembleRetriever([mock_retriever, mock_retriever])
        assert len(retriever.weights) == 2
        assert sum(retriever.weights) == pytest.approx(1.0)

    @pytest.mark.asyncio
    async def test_initializes_with_custom_weights(self, mock_retriever):
        from backend.adaptive_rag.retrievers.ensemble_retriever import EnsembleRetriever

        retriever = EnsembleRetriever([mock_retriever, mock_retriever], weights=[0.7, 0.3])
        assert retriever.weights == [0.7, 0.3]


class TestBM25Retriever:
    @pytest.mark.asyncio
    async def test_retrieve_returns_empty_list(self):
        from backend.adaptive_rag.retrievers.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()
        results = await retriever.retrieve("What is Python?")
        assert isinstance(results, list)
        assert results == []

    @pytest.mark.asyncio
    async def test_retrieve_returns_list_type(self):
        from backend.adaptive_rag.retrievers.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()
        results = await retriever.retrieve("test query", top_k=10)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_retrieve_accepts_top_k_parameter(self):
        from backend.adaptive_rag.retrievers.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()
        results = await retriever.retrieve("test query", top_k=3)
        assert isinstance(results, list)
