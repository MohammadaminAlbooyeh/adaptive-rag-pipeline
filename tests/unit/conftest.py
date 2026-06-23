import sys
from unittest.mock import MagicMock

_MOCK_MODULES = [
    'langchain_anthropic',
    'langchain_openai',
    'langchain_community',
    'chromadb',
    'chromadb.api',
    'chromadb.api.types',
    'duckduckgo_search',
    'rank_bm25',
    'backend.llm.claude_llm',
    'backend.llm.openai_llm',
    'backend.llm.groq_llm',
    'backend.llm.llm_factory',
    'backend.vector_stores',
    'backend.vector_stores.chroma_store',
    'backend.vector_stores.pinecone_store',
    'backend.vector_stores.faiss_store',
    'backend.document_loaders',
    'backend.document_loaders.pdf_loader',
    'backend.document_loaders.txt_loader',
    'backend.document_loaders.csv_loader',
    'backend.document_loaders.docx_loader',
    'backend.document_loaders.url_loader',
    'backend.document_loaders.batch_loader',
    'backend.langchain_components',
    'backend.langchain_components.embeddings',
    'backend.langchain_components.chains',
    'backend.langchain_components.prompts',
    'backend.utils.config',
    'backend.utils.logger',
    'backend.utils.exceptions',
    'backend.utils.validators',
    'backend.utils.helpers',
    'backend.models.database',
]

for mod_name in _MOCK_MODULES:
    sys.modules[mod_name] = MagicMock()

settings_mock = MagicMock()
settings_mock.APP_NAME = "adaptive-rag-pipeline"
sys.modules['backend.utils.config'].settings = settings_mock

logger_mock = MagicMock()
sys.modules['backend.utils.logger'].setup_logger = MagicMock(return_value=logger_mock)

# Pre-create a ClaudeLLM-like class in the mocked module
class MockClaudeLLM:
    def __init__(self, *args, **kwargs):
        pass

    async def generate(self, prompt):
        return "Mocked LLM response"

    async def generate_with_context(self, query, context):
        return f"Based on context: {context[:50]}..."

    async def grade_relevance(self, document, query):
        return True

    async def detect_hallucination(self, answer, context):
        return False

    async def grade_answer(self, answer, context):
        return True

sys.modules['backend.llm.claude_llm'].ClaudeLLM = MockClaudeLLM
