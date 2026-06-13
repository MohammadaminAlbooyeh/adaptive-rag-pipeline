from langchain_community.embeddings import HuggingFaceEmbeddings


class HuggingFaceEmbeddingProvider:
    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(model_name=model)

    def embed_query(self, text: str) -> list:
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: list) -> list:
        return self.embeddings.embed_documents(texts)
