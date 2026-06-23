from typing import List
from backend.vector_stores.base_store import BaseVectorStore
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document


class PineconeStore(BaseVectorStore):
    def __init__(self, index_name: str, embedding_provider: str = "huggingface"):
        self.index_name = index_name
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None

    async def add_documents(self, documents: List[dict]):
        docs = [
            Document(page_content=doc.get("content", ""), metadata=doc.get("metadata", {}))
            for doc in documents
        ]
        self.vector_store = PineconeVectorStore.from_documents(
            docs, self.embeddings, index_name=self.index_name
        )

    async def similarity_search(self, query: str, top_k: int = 5) -> List[dict]:
        if not self.vector_store:
            return []
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
                "source": doc.metadata.get("source", "unknown") if doc.metadata else "unknown",
            })
        return formatted_results
