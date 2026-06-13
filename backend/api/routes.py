from fastapi import APIRouter, HTTPException
from backend.api.schemas import QueryRequest, QueryResponse
from backend.services.adaptive_rag_service import AdaptiveRAGService

router = APIRouter()
rag_service = AdaptiveRAGService()


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    result = await rag_service.process_query(request.text)
    return QueryResponse(**result)


@router.get("/strategies")
async def list_strategies():
    return {"strategies": []}


@router.get("/health")
async def health():
    return {"status": "healthy"}
