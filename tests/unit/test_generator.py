import pytest
from unittest.mock import AsyncMock


class TestAnswerGenerator:
    @pytest.mark.asyncio
    async def test_generate_returns_string(self, answer_generator):
        result = await answer_generator.generate("What is Python?", "Python is a programming language.")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_calls_llm_with_prompt(self, answer_generator):
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value="Python is a programming language.")
        answer_generator.llm = mock_llm

        await answer_generator.generate("What is Python?", "Python is a language.")
        mock_llm.generate.assert_called_once()
        call_args = mock_llm.generate.call_args[0][0]
        assert "What is Python?" in call_args
        assert "Python is a language." in call_args

    @pytest.mark.asyncio
    async def test_generate_with_sources_returns_dict(self, answer_generator, sample_documents):
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value="Python is a programming language.")
        answer_generator.llm = mock_llm

        result = await answer_generator.generate_with_sources("What is Python?", sample_documents)
        assert isinstance(result, dict)
        assert "answer" in result
        assert "sources" in result

    @pytest.mark.asyncio
    async def test_generate_with_sources_lists_sources(self, answer_generator, sample_documents):
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value="Python is a programming language.")
        answer_generator.llm = mock_llm

        result = await answer_generator.generate_with_sources("What is Python?", sample_documents)
        assert len(result["sources"]) == len(sample_documents)
        assert result["sources"] == ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

    @pytest.mark.asyncio
    async def test_generate_with_empty_context(self, answer_generator):
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value="Answer from LLM only.")
        answer_generator.llm = mock_llm

        result = await answer_generator.generate("What is Python?", "")
        assert result == "Answer from LLM only."

    @pytest.mark.asyncio
    async def test_build_context_numbered_documents(self, answer_generator, sample_documents):
        context = answer_generator._build_context(sample_documents)
        assert "[1]" in context
        assert "[2]" in context
        assert "[3]" in context

    @pytest.mark.asyncio
    async def test_build_context_includes_content(self, answer_generator, sample_documents):
        context = answer_generator._build_context(sample_documents)
        assert "Python is a high-level programming language" in context

    @pytest.mark.asyncio
    async def test_build_context_empty_list(self, answer_generator):
        context = answer_generator._build_context([])
        assert context == ""


class TestContextBuilder:
    def test_build_joins_document_content(self, context_builder, sample_documents):
        result = context_builder.build(sample_documents)
        assert isinstance(result, str)
        assert "Python is a high-level programming language" in result

    def test_build_empty_list(self, context_builder):
        result = context_builder.build([])
        assert result == ""

    def test_build_empty_document(self, context_builder):
        docs = [{"content": ""}, {"content": "Only this one has content"}]
        result = context_builder.build(docs)
        assert result == "\n\nOnly this one has content"

    def test_build_preserves_order(self, context_builder):
        docs = [
            {"content": "First document"},
            {"content": "Second document"},
            {"content": "Third document"},
        ]
        result = context_builder.build(docs)
        assert result.index("First") < result.index("Second")
        assert result.index("Second") < result.index("Third")

    def test_build_single_document(self, context_builder, sample_document):
        result = context_builder.build([sample_document])
        assert result == sample_document["content"]

    def test_build_handles_missing_content_key(self, context_builder):
        docs = [{"id": "1"}, {"content": "Has content"}]
        result = context_builder.build(docs)
        assert "Has content" in result


class TestResponseFormatter:
    def test_format_returns_dict(self, response_formatter):
        result = response_formatter.format(
            "Python is a language.",
            ["doc1.pdf", "doc2.pdf"],
            {"strategy": "document_rag", "confidence": 0.85},
        )
        assert isinstance(result, dict)

    def test_format_contains_all_keys(self, response_formatter):
        result = response_formatter.format(
            "Python is a language.",
            ["doc1.pdf"],
            {"strategy": "document_rag", "confidence": 0.85},
        )
        assert "answer" in result
        assert "sources" in result
        assert "metadata" in result

    def test_format_sources_list(self, response_formatter):
        sources = ["doc1.pdf", "doc2.pdf"]
        result = response_formatter.format("Answer.", sources, {})
        assert result["sources"] == sources

    def test_format_metadata(self, response_formatter):
        metadata = {"strategy": "direct_llm", "confidence": 0.95}
        result = response_formatter.format("Answer.", [], metadata)
        assert result["metadata"] == metadata

    def test_format_empty_sources(self, response_formatter):
        result = response_formatter.format("Answer.", [], {})
        assert result["sources"] == []

    def test_format_empty_metadata(self, response_formatter):
        result = response_formatter.format("Answer.", [], {})
        assert result["metadata"] == {}
