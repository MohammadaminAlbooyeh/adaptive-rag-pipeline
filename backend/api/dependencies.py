from backend.services.adaptive_rag_service import AdaptiveRAGService
from backend.services.document_service import DocumentService
from backend.services.cache_service import CacheService


def get_rag_service() -> AdaptiveRAGService:
    return AdaptiveRAGService()


def get_document_service() -> DocumentService:
    return DocumentService()


def get_cache_service() -> CacheService:
    return CacheService()
