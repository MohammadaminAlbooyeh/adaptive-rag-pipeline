import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def sample_query():
    return "What is Python?"


@pytest.fixture
def sample_query_comparative():
    return "Compare Python versus Java for web development"


@pytest.fixture
def sample_query_procedural():
    return "How to install Python on Ubuntu?"


@pytest.fixture
def sample_query_exploratory():
    return "Explain how neural networks work"


@pytest.fixture
def sample_query_opinion():
    return "What is the best programming language for beginners?"


@pytest.fixture
def sample_query_time_sensitive():
    return "What is the latest news about AI today?"


@pytest.fixture
def sample_query_graph():
    return "What are the relationships between entities in the knowledge graph?"


@pytest.fixture
def sample_document():
    return {
        "id": "1",
        "content": "Python is a high-level programming language designed for readability.",
        "source": "doc1.pdf",
        "relevance_score": 0.95,
    }


@pytest.fixture
def sample_documents() -> list:
    return [
        {
            "id": "1",
            "content": "Python is a high-level programming language designed for readability.",
            "source": "doc1.pdf",
            "relevance_score": 0.95,
        },
        {
            "id": "2",
            "content": "Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            "source": "doc2.pdf",
            "relevance_score": 0.87,
        },
        {
            "id": "3",
            "content": "Java is a class-based, object-oriented programming language designed for portability.",
            "source": "doc3.pdf",
            "relevance_score": 0.82,
        },
    ]


@pytest.fixture
def sample_web_results() -> list:
    return [
        {
            "content": "Python is one of the most popular programming languages in 2024.",
            "source": "https://example.com/python",
            "title": "Python Overview",
            "relevance_score": 0.8,
        },
        {
            "content": "Python is widely used in data science, machine learning, and web development.",
            "source": "https://example.com/python-uses",
            "title": "Python Uses",
            "relevance_score": 0.8,
        },
    ]


@pytest.fixture
def mock_llm():
    mock = AsyncMock()
    mock.generate = AsyncMock(return_value="Python is a programming language.")
    mock.generate_with_context = AsyncMock(
        return_value="Based on the context, Python is a programming language."
    )
    mock.grade_relevance = AsyncMock(return_value=True)
    mock.grade_answer = AsyncMock(return_value=True)
    mock.detect_hallucination = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def mock_vector_store():
    mock = MagicMock()
    mock.similarity_search_with_score = MagicMock(
        return_value=[
            (
                MagicMock(
                    page_content="Python is a programming language.",
                    metadata={"source": "doc.pdf"},
                ),
                0.95,
            ),
            (
                MagicMock(
                    page_content="Python supports OOP and functional programming.",
                    metadata={"source": "doc.pdf"},
                ),
                0.87,
            ),
        ]
    )
    mock.similarity_search = MagicMock(
        return_value=[
            MagicMock(
                page_content="Python is a programming language.",
                metadata={"source": "doc.pdf"},
            ),
        ]
    )
    mock.add_documents = AsyncMock()
    mock.delete_by_source = AsyncMock()
    return mock


@pytest.fixture
def mock_retriever():
    retriever = AsyncMock()
    retriever.retrieve = AsyncMock(
        return_value=[
            {
                "content": "Python is a high-level programming language.",
                "source": "doc1.pdf",
                "relevance_score": 0.95,
            },
            {
                "content": "Python supports multiple programming paradigms.",
                "source": "doc2.pdf",
                "relevance_score": 0.87,
            },
        ]
    )
    return retriever


@pytest.fixture
def mock_web_retriever():
    retriever = AsyncMock()
    retriever.retrieve = AsyncMock(
        return_value=[
            {
                "content": "Python is one of the most popular programming languages.",
                "source": "https://example.com/python",
                "relevance_score": 0.8,
            },
        ]
    )
    return retriever


@pytest.fixture
def mock_graph_retriever():
    retriever = AsyncMock()
    retriever.retrieve = AsyncMock(
        return_value=[
            {
                "content": "Python is related to AI and machine learning.",
                "source": "graph://entity/python",
                "relevance_score": 0.9,
            },
        ]
    )
    return retriever


@pytest.fixture
def mock_relevance_grader():
    grader = AsyncMock()
    grader.grade = AsyncMock(
        return_value={
            "score": 0.9,
            "is_relevant": True,
            "explanation": "Graded by mock",
        }
    )
    return grader


@pytest.fixture
def mock_hallucination_grader():
    grader = AsyncMock()
    grader.grade = AsyncMock(
        return_value={"is_grounded": True, "score": 0.95, "explanation": "Mock check"}
    )
    return grader


@pytest.fixture
def mock_answer_grader():
    grader = AsyncMock()
    grader.grade = AsyncMock(
        return_value={
            "quality_score": 0.85,
            "answers_query": True,
            "explanation": "Mock graded",
        }
    )
    return grader


@pytest.fixture
def query_classifier():
    from backend.adaptive_rag.router.query_classifier import QueryClassifier

    return QueryClassifier()


@pytest.fixture
def strategy_selector():
    from backend.adaptive_rag.router.strategy_selector import StrategySelector

    return StrategySelector()


@pytest.fixture
def confidence_scorer():
    from backend.adaptive_rag.router.confidence_scorer import ConfidenceScorer

    return ConfidenceScorer()


@pytest.fixture
def query_router():
    from backend.adaptive_rag.router.query_router import QueryRouter

    return QueryRouter()


@pytest.fixture
def mock_strategy():
    strategy = AsyncMock()
    strategy.name = MagicMock(return_value="direct_llm")
    strategy.description = MagicMock(return_value="Mock strategy")
    strategy.execute = AsyncMock(
        return_value={
            "strategy": "direct_llm",
            "query": "test query",
            "answer": "Mock answer",
            "sources": [],
            "documents": [],
        }
    )
    return strategy


@pytest.fixture
def mock_strategies(mock_strategy, mock_retriever, mock_web_retriever, mock_llm):
    from backend.adaptive_rag.strategies.direct_llm_strategy import DirectLLMStrategy
    from backend.adaptive_rag.strategies.document_rag_strategy import (
        DocumentRAGStrategy,
    )
    from backend.adaptive_rag.strategies.web_search_strategy import WebSearchStrategy
    from backend.adaptive_rag.strategies.hybrid_strategy import HybridStrategy
    from backend.adaptive_rag.strategies.graph_rag_strategy import GraphRAGStrategy

    return {
        "direct_llm": DirectLLMStrategy(mock_llm),
        "document_rag": DocumentRAGStrategy(mock_retriever, mock_llm, AsyncMock()),
        "web_search_rag": WebSearchStrategy(mock_web_retriever, mock_llm),
        "hybrid_rag": HybridStrategy(mock_retriever, mock_web_retriever, mock_llm),
        "graph_rag": GraphRAGStrategy(mock_graph_retriever, mock_llm),
    }


@pytest.fixture
def adaptive_rag_service(mock_strategies):
    from backend.services.adaptive_rag_service import AdaptiveRAGService

    return AdaptiveRAGService(mock_strategies)


@pytest.fixture
def answer_generator(mock_llm):
    from backend.adaptive_rag.generator.answer_generator import AnswerGenerator

    return AnswerGenerator(mock_llm)


@pytest.fixture
def context_builder():
    from backend.adaptive_rag.generator.context_builder import ContextBuilder

    return ContextBuilder()


@pytest.fixture
def response_formatter():
    from backend.adaptive_rag.generator.response_formatter import ResponseFormatter

    return ResponseFormatter()
