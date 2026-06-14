from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.api.schemas import QueryRequest, QueryResponse, DocumentUploadResponse
from backend.services.adaptive_rag_service import AdaptiveRAGService
from backend.services.document_service import DocumentService
from backend.services.indexing_service import IndexingService
from backend.services.analytics_service import AnalyticsService
from backend.llm.claude_llm import ClaudeLLM
from backend.vector_stores.chroma_store import ChromaStore
from backend.adaptive_rag.retrievers.vector_retriever import VectorRetriever
from backend.adaptive_rag.retrievers.web_retriever import WebRetriever
from backend.adaptive_rag.retrievers.graph_retriever import GraphRetriever
from backend.adaptive_rag.strategies.direct_llm_strategy import DirectLLMStrategy
from backend.adaptive_rag.strategies.document_rag_strategy import DocumentRAGStrategy
from backend.adaptive_rag.strategies.web_search_strategy import WebSearchStrategy
from backend.adaptive_rag.strategies.hybrid_strategy import HybridStrategy
from backend.adaptive_rag.strategies.graph_rag_strategy import GraphRAGStrategy
from backend.adaptive_rag.strategies.self_rag_strategy import SelfRAGStrategy
from backend.adaptive_rag.graders.relevance_grader import RelevanceGrader
from backend.adaptive_rag.graders.hallucination_grader import HallucinationGrader
import time

router = APIRouter()

_llm = None
_vector_store = None
_rag_service = None
_document_service = None
_indexing_service = None
_analytics_service = None


def _initialize_services():
    global _llm, _vector_store, _rag_service, _document_service, _indexing_service, _analytics_service

    if _rag_service is not None:
        return

    _llm = ClaudeLLM()
    _vector_store = ChromaStore()
    _analytics_service = AnalyticsService()

    vector_retriever = VectorRetriever(_vector_store)
    web_retriever = WebRetriever()
    graph_retriever = GraphRetriever(_vector_store)
    relevance_grader = RelevanceGrader(_llm)
    hallucination_grader = HallucinationGrader(_llm)

    strategies = {
        "direct_llm": DirectLLMStrategy(_llm),
        "document_rag": DocumentRAGStrategy(vector_retriever, _llm, relevance_grader),
        "web_search_rag": WebSearchStrategy(web_retriever, _llm),
        "hybrid_rag": HybridStrategy(vector_retriever, web_retriever, _llm),
        "graph_rag": GraphRAGStrategy(graph_retriever, _llm),
        "self_rag": SelfRAGStrategy(vector_retriever, _llm, relevance_grader, hallucination_grader),
    }

    _rag_service = AdaptiveRAGService(strategies)
    _document_service = DocumentService(_vector_store)
    _indexing_service = IndexingService(_vector_store, _llm)


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    _initialize_services()
    start_time = time.time()

    try:
        result = await _rag_service.process_query(request.text, top_k=request.top_k)
        latency = time.time() - start_time

        await _analytics_service.log_query(
            query=request.text,
            strategy=result.get("strategy", "unknown"),
            latency=latency,
            confidence=result.get("confidence", 0.0),
        )

        return QueryResponse(
            query=result.get("query", request.text),
            strategy=result.get("strategy", "unknown"),
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0),
            latency=round(latency, 3),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    _initialize_services()

    try:
        content = await file.read()
        result = await _document_service.upload_document(file.filename, content)
        await _indexing_service.index_document(result["id"], file.filename, content)

        return DocumentUploadResponse(
            id=result["id"],
            filename=file.filename,
            status="indexed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents():
    _initialize_services()

    try:
        documents = await _document_service.list_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    _initialize_services()

    try:
        await _document_service.delete_document(doc_id)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def list_strategies():
    _initialize_services()

    return {
        "strategies": [
            {
                "name": "direct_llm",
                "description": "Answer directly using LLM knowledge without retrieval",
            },
            {
                "name": "document_rag",
                "description": "Retrieve relevant documents and generate answer",
            },
            {
                "name": "web_search_rag",
                "description": "Search the web for relevant information",
            },
            {
                "name": "hybrid_rag",
                "description": "Combine document and web search retrieval",
            },
            {
                "name": "graph_rag",
                "description": "Retrieve using knowledge graph relationships",
            },
            {
                "name": "self_rag",
                "description": "Retrieve, critique, and regenerate answers",
            },
        ]
    }


@router.get("/analytics")
async def get_analytics():
    _initialize_services()

    try:
        stats = await _analytics_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "adaptive-rag-pipeline"}
