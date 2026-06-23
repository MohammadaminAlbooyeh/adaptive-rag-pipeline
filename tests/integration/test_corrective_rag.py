import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestCorrectiveRAGWorkflow:
    @pytest.mark.asyncio
    async def test_workflow_initializes(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        assert workflow.llm is mock_llm
        assert workflow.vector_retriever is not None
        assert workflow.web_retriever is not None
        assert workflow.workflow is not None

    @pytest.mark.asyncio
    async def test_retrieve_node_returns_docs(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        workflow.vector_retriever.retrieve = AsyncMock(
            return_value=[{"content": "Python is a language.", "source": "doc.pdf"}]
        )

        state = {"query": "What is Python?", "documents": [], "grade": "", "corrected_docs": [], "answer": ""}
        result = await workflow._retrieve(state)
        assert "documents" in result
        assert len(result["documents"]) > 0

    @pytest.mark.asyncio
    async def test_grade_node_returns_correct_when_low_relevance(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        workflow.relevance_grader.grade = AsyncMock(
            return_value={"score": 0.3, "is_relevant": False}
        )

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Java is a language.", "source": "doc.pdf"}],
            "grade": "",
            "corrected_docs": [],
            "answer": "",
        }
        result = await workflow._grade(state)
        assert result["grade"] == "correct"

    @pytest.mark.asyncio
    async def test_grade_node_returns_generate_when_high_relevance(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        workflow.relevance_grader.grade = AsyncMock(
            return_value={"score": 0.9, "is_relevant": True}
        )

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "grade": "",
            "corrected_docs": [],
            "answer": "",
        }
        result = await workflow._grade(state)
        assert result["grade"] == "generate"

    @pytest.mark.asyncio
    async def test_grade_node_returns_correct_when_empty_docs(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        state = {"query": "What is Python?", "documents": [], "grade": "", "corrected_docs": [], "answer": ""}
        result = await workflow._grade(state)
        assert result["grade"] == "correct"

    @pytest.mark.asyncio
    async def test_correct_node_adds_web_results(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        workflow.web_retriever.retrieve = AsyncMock(
            return_value=[
                {"content": "Python is popular on the web.", "source": "https://example.com"}
            ]
        )

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "grade": "correct",
            "corrected_docs": [],
            "answer": "",
        }
        result = await workflow._correct(state)
        assert "corrected_docs" in result
        assert len(result["corrected_docs"]) > 0

    @pytest.mark.asyncio
    async def test_correct_node_deduplicates_sources(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        workflow.web_retriever.retrieve = AsyncMock(
            return_value=[
                {"content": "Web result", "source": "doc.pdf"}
            ]
        )

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Doc result", "source": "doc.pdf"}],
            "grade": "correct",
            "corrected_docs": [],
            "answer": "",
        }
        result = await workflow._correct(state)
        # The web result has same source as existing doc, so it should be filtered
        assert len(result["corrected_docs"]) == len(state["documents"])

    @pytest.mark.asyncio
    async def test_generate_node_with_corrected_docs(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        mock_llm.generate = AsyncMock(return_value="Python is a programming language.")

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "corrected_docs": [{"content": "Python is widely used.", "source": "doc.pdf"}],
            "grade": "correct",
            "answer": "",
        }
        result = await workflow._generate(state)
        assert "answer" in result
        assert result["answer"] == "Python is a programming language."

    @pytest.mark.asyncio
    async def test_generate_node_without_context(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        mock_llm.generate = AsyncMock(return_value="Direct LLM answer.")

        state = {
            "query": "What is Python?",
            "documents": [],
            "corrected_docs": [],
            "grade": "",
            "answer": "",
        }
        result = await workflow._generate(state)
        assert result["answer"] == "Direct LLM answer."

    def test_decide_returns_state_grade(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        assert workflow._decide({"grade": "generate"}) == "generate"
        assert workflow._decide({"grade": "correct"}) == "correct"
        assert workflow._decide({}) == "generate"

    @pytest.mark.asyncio
    async def test_run_returns_result_dict(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.corrective_rag_workflow import CorrectiveRAGWorkflow

        workflow = CorrectiveRAGWorkflow(mock_llm, mock_vector_store)
        workflow.workflow.ainvoke = AsyncMock(
            return_value={
                "query": "What is Python?",
                "documents": [{"content": "Python is a language."}],
                "grade": "generate",
                "corrected_docs": [],
                "answer": "Python is a programming language.",
            }
        )

        result = await workflow.run("What is Python?")
        assert isinstance(result, dict)
        assert "query" in result
        assert "answer" in result
        assert result["answer"] == "Python is a programming language."
