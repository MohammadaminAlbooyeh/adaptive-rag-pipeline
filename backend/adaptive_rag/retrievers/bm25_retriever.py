from typing import List
from backend.adaptive_rag.retrievers.base_retriever import BaseRetriever
from rank_bm25 import BM25Okapi


class BM25Retriever(BaseRetriever):
    def __init__(self, documents: List[dict] = None):
        self.documents = documents or []
        self._tokenized_corpus = None
        self._bm25 = None
        if documents:
            self._initialize_bm25()

    def _initialize_bm25(self):
        self._tokenized_corpus = [
            doc.get("content", "").split() for doc in self.documents
        ]
        self._bm25 = BM25Okapi(self._tokenized_corpus)

    def update_documents(self, documents: List[dict]):
        self.documents = documents
        self._initialize_bm25()

    async def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        if not self._bm25 or not self.documents:
            return []

        tokenized_query = query.split()
        scores = self._bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
            :top_k
        ]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                doc = dict(self.documents[idx])
                doc["relevance_score"] = float(scores[idx])
                results.append(doc)

        return results
