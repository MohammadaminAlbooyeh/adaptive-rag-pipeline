from typing import List
from backend.vector_stores.base_store import BaseVectorStore
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import asyncio


class FAISSStore(BaseVectorStore):
    def __init__(self, persist_directory: str = "./faiss_index"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self._initialize_faiss()

    def _initialize_faiss(self):
        try:
            self.vector_store = FAISS.from_documents(
                [Document(page_content="init")], self.embeddings
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize FAISS: {str(e)}")

    async def add_documents(self, documents: List[dict]):
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._sync_add_documents, documents)
        except Exception as e:
            raise RuntimeError(f"Failed to add documents to FAISS: {str(e)}")

    def _sync_add_documents(self, documents: List[dict]):
        docs = [
            Document(
                page_content=doc.get("content", ""), metadata=doc.get("metadata", {})
            )
            for doc in documents
        ]
        self.vector_store.add_documents(docs)

    async def similarity_search(self, query: str, top_k: int = 5) -> List[dict]:
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, self._sync_similarity_search, query, top_k
            )
            return results
        except Exception as e:
            raise RuntimeError(f"FAISS similarity search failed: {str(e)}")

    def _sync_similarity_search(self, query: str, top_k: int) -> List[dict]:
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        formatted_results = []
        for doc, score in results:
            formatted_results.append(
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                    "source": doc.metadata.get("source", "unknown")
                    if doc.metadata
                    else "unknown",
                }
            )
        return formatted_results
