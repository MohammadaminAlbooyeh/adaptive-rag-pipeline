from typing import List
from backend.adaptive_rag.retrievers.base_retriever import BaseRetriever
import asyncio


class GraphRetriever(BaseRetriever):
    def __init__(self, vector_store):
        self.vector_store = vector_store

    async def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self._sync_retrieve, query, top_k)
            return results
        except Exception as e:
            raise RuntimeError(f"Graph retrieval failed: {str(e)}")

    def _sync_retrieve(self, query: str, top_k: int) -> List[dict]:
        entities = self._extract_entities(query)
        if not entities:
            return []

        all_results = []
        for entity in entities:
            try:
                results = self.vector_store.similarity_search(entity, k=top_k // len(entities) + 1)
                all_results.extend(results)
            except Exception:
                pass

        return all_results[:top_k]

    def _extract_entities(self, query: str) -> List[str]:
        words = query.split()
        important_words = [w for w in words if len(w) > 3 and w.upper() == w or w[0].isupper()]
        return important_words[:3]
