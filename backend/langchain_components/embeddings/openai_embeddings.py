from langchain_openai import OpenAIEmbeddings


class OpenAIEmbeddingProvider:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.embeddings = OpenAIEmbeddings(model=model)

    def embed_query(self, text: str) -> list:
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: list) -> list:
        return self.embeddings.embed_documents(texts)
