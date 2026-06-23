import pytest
from unittest.mock import AsyncMock, MagicMock


class TestAdaptiveWorkflow:
    @pytest.mark.asyncio
    async def test_workflow_initializes_with_dependencies(
        self, mock_llm, mock_vector_store
    ):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        assert workflow.llm is mock_llm
        assert workflow.vector_store is mock_vector_store
        assert workflow.max_iterations == 3
        assert workflow.workflow is not None

    @pytest.mark.asyncio
    async def test_classify_query_node(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        state = {
            "query": "What is Python?",
            "query_type": "",
            "strategy": "",
            "documents": [],
            "web_results": [],
            "answer": "",
            "grade": "",
            "answer_quality": "",
            "generation_count": 0,
            "web_search_count": 0,
        }
        result = await workflow._classify_query(state)
        assert "query_type" in result
        assert "strategy" in result
        assert result["query_type"] == "factual"

    @pytest.mark.asyncio
    async def test_route_query_node(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        state = {"strategy": "document_rag", "query": "What is Python?"}
        result = await workflow._route_query(state)
        assert result["strategy"] == "document_rag"

    @pytest.mark.asyncio
    async def test_retrieve_documents_node(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        workflow.vector_retriever.retrieve = AsyncMock(
            return_value=[{"content": "Python is a language.", "source": "doc.pdf"}]
        )

        state = {
            "query": "What is Python?",
            "documents": [],
            "generation_count": 0,
            "web_results": [],
            "answer": "",
            "grade": "",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "web_search_count": 0,
        }
        result = await workflow._retrieve_documents(state)
        assert "documents" in result
        assert len(result["documents"]) > 0

    @pytest.mark.asyncio
    async def test_retrieve_documents_respects_max_iterations(
        self, mock_llm, mock_vector_store
    ):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        state = {
            "query": "What is Python?",
            "documents": [{"content": "existing doc"}],
            "generation_count": 3,
            "web_results": [],
            "answer": "",
            "grade": "",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "web_search_count": 0,
        }
        result = await workflow._retrieve_documents(state)
        assert result["documents"] == state["documents"]

    @pytest.mark.asyncio
    async def test_grade_documents_relevant(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        workflow.relevance_grader.grade = AsyncMock(
            return_value={"score": 0.9, "is_relevant": True, "explanation": "Relevant"}
        )

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "web_results": [],
            "answer": "",
            "grade": "",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "generation_count": 0,
            "web_search_count": 0,
        }
        result = await workflow._grade_documents(state)
        assert result["grade"] == "relevant"

    @pytest.mark.asyncio
    async def test_grade_documents_not_relevant(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        workflow.relevance_grader.grade = AsyncMock(
            return_value={
                "score": 0.1,
                "is_relevant": False,
                "explanation": "Not relevant",
            }
        )

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Java is a language.", "source": "doc.pdf"}],
            "web_results": [],
            "answer": "",
            "grade": "",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "generation_count": 0,
            "web_search_count": 0,
        }
        result = await workflow._grade_documents(state)
        assert result["grade"] == "not_relevant"

    @pytest.mark.asyncio
    async def test_grade_documents_empty_list(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        state = {
            "query": "What is Python?",
            "documents": [],
            "grade": "",
            "web_results": [],
            "answer": "",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "generation_count": 0,
            "web_search_count": 0,
        }
        result = await workflow._grade_documents(state)
        assert result["grade"] == "not_relevant"

    @pytest.mark.asyncio
    async def test_generate_answer(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        mock_llm.generate = AsyncMock(return_value="Python is a programming language.")

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "web_results": [],
            "answer": "",
            "grade": "",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "generation_count": 0,
            "web_search_count": 0,
        }
        result = await workflow._generate_answer(state)
        assert "answer" in result
        assert "generation_count" in result
        assert result["generation_count"] == 1

    @pytest.mark.asyncio
    async def test_generate_answer_with_web_results(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        state = {
            "query": "What is Python?",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "web_results": [{"content": "Python is popular.", "source": "web"}],
            "answer": "",
            "query_type": "",
            "strategy": "",
            "grade": "",
            "answer_quality": "",
            "generation_count": 0,
            "web_search_count": 0,
        }
        result = await workflow._generate_answer(state)
        assert len(result["answer"]) > 0

    @pytest.mark.asyncio
    async def test_grade_answer_good(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        workflow.hallucination_grader.grade = AsyncMock(
            return_value={"is_grounded": True, "score": 0.95}
        )
        workflow.answer_grader.grade = AsyncMock(
            return_value={"quality_score": 0.9, "answers_query": True}
        )

        state = {
            "query": "What is Python?",
            "answer": "Python is a programming language.",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "web_results": [],
            "grade": "relevant",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "generation_count": 1,
            "web_search_count": 0,
        }
        result = await workflow._grade_answer(state)
        assert result["answer_quality"] == "good"

    @pytest.mark.asyncio
    async def test_grade_answer_hallucination(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        workflow.hallucination_grader.grade = AsyncMock(
            return_value={"is_grounded": False, "score": 0.2}
        )

        state = {
            "query": "What is Python?",
            "answer": "Python is a mythical creature.",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "web_results": [],
            "grade": "relevant",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "generation_count": 1,
            "web_search_count": 0,
        }
        result = await workflow._grade_answer(state)
        assert result["answer_quality"] == "hallucination"

    @pytest.mark.asyncio
    async def test_grade_answer_not_useful(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        workflow.hallucination_grader.grade = AsyncMock(
            return_value={"is_grounded": True, "score": 0.95}
        )
        workflow.answer_grader.grade = AsyncMock(
            return_value={"quality_score": 0.3, "answers_query": False}
        )

        state = {
            "query": "What is Python?",
            "answer": "I don't know.",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "web_results": [],
            "grade": "relevant",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "generation_count": 1,
            "web_search_count": 0,
        }
        result = await workflow._grade_answer(state)
        assert result["answer_quality"] == "not_useful"

    @pytest.mark.asyncio
    async def test_rewrite_query(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        # Mock query_rewriter to return a rewritten query
        workflow.query_rewriter.rewrite = AsyncMock(return_value="What is Python?")
        state = {
            "query": "What is Python?",
            "generation_count": 0,
            "documents": [],
            "web_results": [],
            "answer": "",
            "grade": "",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "web_search_count": 0,
        }
        result = await workflow._rewrite_query(state)
        assert "query" in result
        # When rewrite returns the same query, the code appends " (refined)"
        assert "(refined)" in result["query"]

    @pytest.mark.asyncio
    async def test_web_search_node(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        workflow.web_retriever.retrieve = AsyncMock(
            return_value=[
                {"content": "Python is popular.", "source": "web", "title": "Python"}
            ]
        )

        state = {
            "query": "What is Python?",
            "web_results": [],
            "web_search_count": 0,
            "documents": [],
            "answer": "",
            "grade": "",
            "answer_quality": "",
            "query_type": "",
            "strategy": "",
            "generation_count": 0,
        }
        result = await workflow._web_search(state)
        assert "web_results" in result
        assert "web_search_count" in result
        assert result["web_search_count"] == 1

    def test_decide_route_returns_simple(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        assert workflow._decide_route({}) == "simple"

    def test_decide_grade_respects_max_iterations(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        state = {"generation_count": 3, "grade": "not_relevant"}
        assert workflow._decide_grade(state) == "relevant"

    def test_decide_grade_returns_state_grade(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        state = {"generation_count": 0, "grade": "relevant"}
        assert workflow._decide_grade(state) == "relevant"

    def test_decide_answer_quality(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        assert workflow._decide_answer_quality({"answer_quality": "good"}) == "good"
        assert (
            workflow._decide_answer_quality({"answer_quality": "hallucination"})
            == "hallucination"
        )
        assert (
            workflow._decide_answer_quality({"answer_quality": "not_useful"})
            == "not_useful"
        )
        assert workflow._decide_answer_quality({}) == "good"

    @pytest.mark.asyncio
    async def test_run_returns_formatted_result(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.adaptive_workflow import (
            AdaptiveWorkflow,
        )

        workflow = AdaptiveWorkflow(mock_llm, mock_vector_store)
        mock_llm.generate = AsyncMock(return_value="Python is a programming language.")

        # Mock the workflow.ainvoke to return a realistic state
        workflow.workflow.ainvoke = AsyncMock(
            return_value={
                "query": "What is Python?",
                "query_type": "factual",
                "strategy": "document_rag",
                "documents": [
                    {"content": "Python is a language.", "source": "doc.pdf"}
                ],
                "web_results": [],
                "answer": "Python is a programming language.",
                "grade": "relevant",
                "answer_quality": "good",
                "generation_count": 1,
                "web_search_count": 0,
            }
        )

        result = await workflow.run("What is Python?")
        assert isinstance(result, dict)
        assert "answer" in result
        assert "sources" in result
        assert "metadata" in result
        assert result["answer"] == "Python is a programming language."
