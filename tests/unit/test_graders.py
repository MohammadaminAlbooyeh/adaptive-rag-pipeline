import pytest
from unittest.mock import AsyncMock, MagicMock


class TestRelevanceGrader:
    @pytest.mark.asyncio
    async def test_grade_without_llm_returns_dict(self):
        from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader

        grader = RelevanceGrader()
        result = await grader.grade("Python is a programming language.", "What is Python?")
        assert isinstance(result, dict)
        assert "score" in result
        assert "is_relevant" in result
        assert "explanation" in result

    @pytest.mark.asyncio
    async def test_grade_without_llm_detects_relevance(self):
        from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader

        grader = RelevanceGrader()
        result = await grader.grade("Python is a programming language.", "Python")
        assert result["is_relevant"] is True
        assert result["score"] > 0.5

    @pytest.mark.asyncio
    async def test_grade_without_llm_detects_irrelevant(self):
        from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader

        grader = RelevanceGrader()
        result = await grader.grade("The sky is blue and clouds are white.", "What is Python?")
        assert result["is_relevant"] is False
        assert result["score"] < 0.5

    @pytest.mark.asyncio
    async def test_grade_with_llm(self):
        from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader

        llm = AsyncMock()
        llm.grade_relevance = AsyncMock(return_value=True)
        grader = RelevanceGrader(llm)
        result = await grader.grade("Python is a language.", "What is Python?")
        assert result["is_relevant"] is True
        assert result["score"] == 1.0
        assert result["explanation"] == "Graded by LLM"

    @pytest.mark.asyncio
    async def test_grade_with_llm_not_relevant(self):
        from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader

        llm = AsyncMock()
        llm.grade_relevance = AsyncMock(return_value=False)
        grader = RelevanceGrader(llm)
        result = await grader.grade("Python is a language.", "What is Java?")
        assert result["is_relevant"] is False
        assert result["score"] == 0.0

    @pytest.mark.asyncio
    async def test_empty_query_returns_zero(self):
        from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader

        grader = RelevanceGrader()
        result = await grader.grade("Some document content.", "")
        assert result["score"] == 0.0
        assert result["is_relevant"] is False

    @pytest.mark.asyncio
    async def test_partial_relevance_scoring(self):
        from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader

        grader = RelevanceGrader()
        result = await grader.grade("Python programming Java development", "Python Java")
        assert 0.0 < result["score"] <= 1.0

    @pytest.mark.asyncio
    async def test_explanation_without_llm(self):
        from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader

        grader = RelevanceGrader()
        result = await grader.grade("Python is a language.", "Python")
        assert result["explanation"] == "Computed by keyword matching"

    @pytest.mark.asyncio
    async def test_keyword_overlap_score(self):
        from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader

        grader = RelevanceGrader()
        result = await grader.grade("Python Java C++", "Python Java C++ Rust")
        assert result["score"] == 0.75


class TestHallucinationGrader:
    @pytest.mark.asyncio
    async def test_grade_without_llm_returns_dict(self):
        from backend.adaptive_rag.graders.hallucination_grader import HallucinationGrader

        grader = HallucinationGrader()
        result = await grader.grade("Python is a language.", "Python is a programming language.")
        assert isinstance(result, dict)
        assert "is_grounded" in result
        assert "score" in result

    @pytest.mark.asyncio
    async def test_grade_without_llm_grounded(self):
        from backend.adaptive_rag.graders.hallucination_grader import HallucinationGrader

        grader = HallucinationGrader()
        result = await grader.grade("Python is a language.", "Python is a language")
        assert result["is_grounded"] is True
        assert result["score"] > 0.5

    @pytest.mark.asyncio
    async def test_grade_without_llm_not_grounded(self):
        from backend.adaptive_rag.graders.hallucination_grader import HallucinationGrader

        grader = HallucinationGrader()
        result = await grader.grade("Rustans are mythical creatures.", "Python is a programming language.")
        assert result["is_grounded"] is False

    @pytest.mark.asyncio
    async def test_grade_with_empty_context(self):
        from backend.adaptive_rag.graders.hallucination_grader import HallucinationGrader

        grader = HallucinationGrader()
        result = await grader.grade("Python is a language.", "")
        assert result["score"] == 0.0
        assert result["is_grounded"] is False

    @pytest.mark.asyncio
    async def test_grade_with_empty_answer(self):
        from backend.adaptive_rag.graders.hallucination_grader import HallucinationGrader

        grader = HallucinationGrader()
        result = await grader.grade("", "Python is a programming language.")
        assert result["score"] == 1.0
        assert result["is_grounded"] is True

    @pytest.mark.asyncio
    async def test_grade_with_llm_not_grounded(self):
        from backend.adaptive_rag.graders.hallucination_grader import HallucinationGrader

        llm = AsyncMock()
        llm.detect_hallucination = AsyncMock(return_value=True)
        grader = HallucinationGrader(llm)
        result = await grader.grade("Fake answer.", "Real context.")
        assert result["is_grounded"] is False
        assert result["score"] == 0.0

    @pytest.mark.asyncio
    async def test_grade_with_llm_grounded(self):
        from backend.adaptive_rag.graders.hallucination_grader import HallucinationGrader

        llm = AsyncMock()
        llm.detect_hallucination = AsyncMock(return_value=False)
        grader = HallucinationGrader(llm)
        result = await grader.grade("Real answer.", "Real context.")
        assert result["is_grounded"] is True
        assert result["score"] == 1.0


class TestAnswerGrader:
    @pytest.mark.asyncio
    async def test_grade_without_llm_returns_dict(self):
        from backend.adaptive_rag.graders.answer_grader import AnswerGrader

        grader = AnswerGrader()
        result = await grader.grade("Python is a programming language.", "Context about Python.")
        assert isinstance(result, dict)
        assert "quality_score" in result
        assert "answers_query" in result
        assert "explanation" in result

    @pytest.mark.asyncio
    async def test_grade_without_llm_long_answer(self):
        from backend.adaptive_rag.graders.answer_grader import AnswerGrader

        grader = AnswerGrader()
        result = await grader.grade(
            "Python is a programming language. It is used for web development and data science "
            "because of its readability.", "Context about Python."
        )
        assert result["quality_score"] > 0.5
        assert result["answers_query"] is True

    @pytest.mark.asyncio
    async def test_grade_without_llm_short_answer(self):
        from backend.adaptive_rag.graders.answer_grader import AnswerGrader

        grader = AnswerGrader()
        result = await grader.grade("Yes.", "Context.")
        assert result["quality_score"] < 0.5
        assert result["answers_query"] is False

    @pytest.mark.asyncio
    async def test_grade_empty_answer(self):
        from backend.adaptive_rag.graders.answer_grader import AnswerGrader

        grader = AnswerGrader()
        result = await grader.grade("", "Some context.")
        assert result["quality_score"] == 0.0
        assert result["answers_query"] is False

    @pytest.mark.asyncio
    async def test_grade_with_llm(self):
        from backend.adaptive_rag.graders.answer_grader import AnswerGrader

        llm = AsyncMock()
        llm.grade_answer = AsyncMock(return_value=True)
        grader = AnswerGrader(llm)
        result = await grader.grade("Good answer.", "Good context.")
        assert result["quality_score"] == 1.0
        assert result["answers_query"] is True

    @pytest.mark.asyncio
    async def test_grade_with_llm_not_answering(self):
        from backend.adaptive_rag.graders.answer_grader import AnswerGrader

        llm = AsyncMock()
        llm.grade_answer = AsyncMock(return_value=False)
        grader = AnswerGrader(llm)
        result = await grader.grade("Bad answer.", "Good context.")
        assert result["quality_score"] == 0.5
        assert result["answers_query"] is False

    @pytest.mark.asyncio
    async def test_quality_score_punctuation_bonus(self):
        from backend.adaptive_rag.graders.answer_grader import AnswerGrader

        grader = AnswerGrader()
        with_punct = await grader.grade("Python is a language. It is used widely.", "ctx")
        without_punct = await grader.grade("Python is a language", "ctx")
        assert with_punct["quality_score"] > without_punct["quality_score"]

    @pytest.mark.asyncio
    async def test_quality_score_reasoning_bonus(self):
        from backend.adaptive_rag.graders.answer_grader import AnswerGrader

        grader = AnswerGrader()
        with_reasoning = await grader.grade(
            "Python is popular because it is easy to read. Therefore many use it.", "ctx"
        )
        without = await grader.grade("Python is popular.", "ctx")
        assert with_reasoning["quality_score"] > without["quality_score"]


class TestQueryRewriter:
    @pytest.mark.asyncio
    async def test_rewrite_returns_string(self):
        from backend.adaptive_rag.graders.query_rewriter import QueryRewriter

        rewriter = QueryRewriter()
        result = await rewriter.rewrite("What is Python?")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_rewrite_returns_same_query_without_llm(self):
        from backend.adaptive_rag.graders.query_rewriter import QueryRewriter

        rewriter = QueryRewriter()
        result = await rewriter.rewrite("What is Python?")
        assert result == "What is Python?"

    @pytest.mark.asyncio
    async def test_rewrite_with_feedback(self):
        from backend.adaptive_rag.graders.query_rewriter import QueryRewriter

        rewriter = QueryRewriter()
        result = await rewriter.rewrite("What is Python?", "Need more detail")
        assert result == "What is Python?"

    @pytest.mark.asyncio
    async def test_rewrite_empty_query(self):
        from backend.adaptive_rag.graders.query_rewriter import QueryRewriter

        rewriter = QueryRewriter()
        result = await rewriter.rewrite("")
        assert result == ""

    @pytest.mark.asyncio
    async def test_rewrite_with_llm(self):
        from backend.adaptive_rag.graders.query_rewriter import QueryRewriter

        llm = AsyncMock()
        llm.generate = AsyncMock(return_value="What is Python programming language?")
        rewriter = QueryRewriter(llm=llm)
        result = await rewriter.rewrite("What is Python?")
        assert isinstance(result, str)
        llm.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_rewrite_with_llm_returns_original_on_empty_response(self):
        from backend.adaptive_rag.graders.query_rewriter import QueryRewriter

        llm = AsyncMock()
        llm.generate = AsyncMock(return_value="")
        rewriter = QueryRewriter(llm=llm)
        result = await rewriter.rewrite("What is Python?")
        assert result == "What is Python?"
