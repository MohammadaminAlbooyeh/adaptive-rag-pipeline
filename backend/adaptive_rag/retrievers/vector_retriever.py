from typing import List
from backend.adaptive_rag.retrievers.base_retriever import BaseRetriever
import asyncio


class VectorRetriever(BaseRetriever):
    def __init__(self, vector_store):
        self.vector_store = vector_store

    async def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, self._sync_retrieve, query, top_k
            )
            return results
        except Exception as e:
            raise RuntimeError(f"Vector retrieval failed: {str(e)}")

    def _sync_retrieve(self, query: str, top_k: int) -> List[dict]:
        if not hasattr(self.vector_store, "similarity_search_with_score"):
            return []

        try:
            results = self.vector_store.similarity_search_with_score(query, k=top_k)
            retrieved_docs = []
            for doc, score in results:
                retrieved_docs.append(
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "relevance_score": float(score),
                        "source": doc.metadata.get("source", "unknown")
                        if doc.metadata
                        else "unknown",
                    }
                )
            return retrieved_docs
        except Exception as e:
            raise RuntimeError(f"Vector similarity search failed: {str(e)}")
