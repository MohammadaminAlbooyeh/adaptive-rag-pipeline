from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Adaptive RAG Pipeline"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    EMBEDDING_PROVIDER: str = "openai"
    VECTOR_STORE_TYPE: str = "chroma"
    CHROMA_PERSIST_DIR: str = "./chromadb"

    SEARCH_PROVIDER: str = "duckduckgo"
    DATABASE_URL: str = ""
    REDIS_URL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
