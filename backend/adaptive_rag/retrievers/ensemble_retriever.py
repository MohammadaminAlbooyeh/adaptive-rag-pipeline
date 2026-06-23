from typing import List
from backend.adaptive_rag.retrievers.base_retriever import BaseRetriever


class EnsembleRetriever(BaseRetriever):
    def __init__(self, retrievers: List[BaseRetriever], weights: List[float] = None):
        self.retrievers = retrievers
        self.weights = weights or [1.0 / len(retrievers)] * len(retrievers)

    async def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        all_results = []
        for retriever in self.retrievers:
            results = await retriever.retrieve(query, top_k)
            all_results.extend(results)

        seen_sources = set()
        deduped = []
        for doc in all_results:
            source = doc.get("source", doc.get("content", ""))[:100]
            if source not in seen_sources:
                seen_sources.add(source)
                deduped.append(doc)

        return deduped[:top_k]
