class LocalEmbeddingProvider:
    def embed_query(self, text: str) -> list:
        return [0.0] * 384

    def embed_documents(self, texts: list) -> list:
        return [[0.0] * 384 for _ in texts]
