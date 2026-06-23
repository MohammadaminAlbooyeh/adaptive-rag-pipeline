import pytest
from unittest.mock import AsyncMock, MagicMock


class TestSelfRAGWorkflow:
    @pytest.mark.asyncio
    async def test_workflow_initializes(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)
        assert workflow.llm is mock_llm
        assert workflow.vector_retriever is not None
        assert workflow.max_iterations == 3

    @pytest.mark.asyncio
    async def test_retrieve_node_returns_documents(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)
        workflow.vector_retriever.retrieve = AsyncMock(
            return_value=[{"content": "Python is a language.", "source": "doc.pdf"}]
        )

        state = {"query": "What is Python?", "documents": [], "reflection": "", "answer": "", "iteration": 0}
        result = await workflow._retrieve(state)
        assert "documents" in result
        assert "iteration" in result
        assert result["iteration"] == 1

    @pytest.mark.asyncio
    async def test_retrieve_respects_max_iterations(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)
        state = {"query": "What is Python?", "documents": [{"content": "existing"}], "reflection": "", "answer": "", "iteration": 3}
        result = await workflow._retrieve(state)
        assert result["documents"] == state["documents"]

    @pytest.mark.asyncio
    async def test_reflect_node_with_relevant_docs(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)
        workflow.relevance_grader.grade = AsyncMock(
            return_value={"is_relevant": True, "score": 0.9, "explanation": "Relevant"}
        )

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "reflection": "",
            "answer": "",
            "iteration": 1,
        }
        result = await workflow._reflect(state)
        assert result["reflection"] == "All documents are relevant."

    @pytest.mark.asyncio
    async def test_reflect_node_with_irrelevant_docs(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)
        workflow.relevance_grader.grade = AsyncMock(
            return_value={"is_relevant": False, "score": 0.1, "explanation": "Not relevant"}
        )

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Java is a language.", "source": "doc.pdf"}],
            "reflection": "",
            "answer": "",
            "iteration": 1,
        }
        result = await workflow._reflect(state)
        assert "not relevant" in result["reflection"]

    @pytest.mark.asyncio
    async def test_generate_node_with_context(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)
        mock_llm.generate = AsyncMock(return_value="Python is a programming language.")

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
            "reflection": "All documents are relevant.",
            "answer": "",
            "iteration": 1,
        }
        result = await workflow._generate(state)
        assert "answer" in result
        assert result["answer"] == "Python is a programming language."

    @pytest.mark.asyncio
    async def test_generate_node_without_context(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)
        mock_llm.generate = AsyncMock(return_value="Direct LLM answer.")

        state = {
            "query": "What is Python?",
            "documents": [],
            "reflection": "",
            "answer": "",
            "iteration": 1,
        }
        result = await workflow._generate(state)
        assert result["answer"] == "Direct LLM answer."

    def test_decide_generates_after_max_iterations(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)
        state = {"iteration": 3, "query": "test", "documents": [], "reflection": "", "answer": ""}
        assert workflow._decide(state) == "generate"

    def test_decide_reflects_within_iterations(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)
        state = {"iteration": 1, "query": "test", "documents": [], "reflection": "", "answer": ""}
        assert workflow._decide(state) == "reflect"

    @pytest.mark.asyncio
    async def test_run_returns_state_dict(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)

        # Mock the compiled workflow
        workflow.workflow.ainvoke = AsyncMock(
            return_value={
                "query": "What is Python?",
                "documents": [{"content": "Python is a language.", "source": "doc.pdf"}],
                "reflection": "All documents are relevant.",
                "answer": "Python is a programming language.",
                "iteration": 1,
            }
        )

        result = await workflow.run("What is Python?")
        assert isinstance(result, dict)
        assert "query" in result
        assert "answer" in result
        assert "documents" in result
        assert "reflection" in result

    @pytest.mark.asyncio
    async def test_reflect_rewrites_query_with_feedback(self, mock_llm, mock_vector_store):
        from backend.adaptive_rag.langgraph_workflows.self_rag_workflow import SelfRAGWorkflow

        workflow = SelfRAGWorkflow(mock_llm, mock_vector_store)
        workflow.relevance_grader.grade = AsyncMock(
            return_value={"is_relevant": False, "score": 0.1}
        )
        # Override query_rewriter to return a different query
        mock_rewriter = MagicMock()
        mock_rewriter.rewrite = MagicMock(return_value="What is Python programming?")
        workflow.query_rewriter = mock_rewriter

        state = {
            "query": "What is Python?",
            "documents": [{"content": "Java is a language.", "source": "doc.pdf"}],
            "reflection": "",
            "answer": "",
            "iteration": 1,
        }
        result = await workflow._reflect(state)
        assert result["query"] == "What is Python programming?"
