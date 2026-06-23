# Architecture

## System Overview

The Adaptive RAG Pipeline is a modular, strategy-driven Retrieval-Augmented Generation (RAG) system that intelligently routes queries to the most appropriate retrieval and generation strategy based on query characteristics. It combines traditional vector search, web search, knowledge graph traversal, and self-reflective loops into a unified pipeline.

### Design Philosophy

- **Adaptive Routing**: Queries are classified at runtime and routed to the optimal strategy — no manual strategy selection needed.
- **Pluggable Components**: Every major subsystem (LLM, vector store, retriever, strategy) is an abstract base class with multiple implementations.
- **Quality Assurance**: Graders validate relevance, hallucination, and answer quality at multiple stages.
- **Stateful Workflows**: LangGraph state machines orchestrate multi-step processes with conditional branching and retry loops.
- **Observability**: Every query is logged with strategy, latency, and confidence for analytics.

---

## System Architecture Diagram

```
+------------------------------------------------------------------+
|                         Client / Frontend                         |
+------------------------------------------------------------------+
                              |  HTTP
                              v
+------------------------------------------------------------------+
|                      FastAPI Application                          |
|  +------------------+  +------------------+  +------------------+ |
|  |   API Routes     |  |    Middleware     |  |  API Schemas     | |
|  |  (api/routes.py) |  | (api/middleware.py)| | (api/schemas.py) | |
|  +------------------+  +------------------+  +------------------+ |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|                     AdaptiveRAGService                            |
|  (services/adaptive_rag_service.py)                               |
|  Orchestrates: classify -> select -> execute -> score             |
+------------------------------------------------------------------+
         |
         +----------------+----------------+----------------+
         |                |                |                |
         v                v                v                v
+----------------+ +----------------+ +----------------+ +----------------+
| QueryClassifier| |StrategySelector| |  Strategies   | |ConfidenceScorer|
| (router/)      | | (router/)      | | (strategies/) | | (router/)      |
| Determines     | | Maps classify  | | Pluggable     | | Scores result  |
| query_type,    | | to strategy    | | execution     | | based on       |
| complexity,    | | name           | | engines       | | sources & type |
| needs_docs/web | |                | |               | |                |
+----------------+ +----------------+ +----------------+ +----------------+
                                               |
                    +--------------------------+--------------------------+
                    |                          |                          |
                    v                          v                          v
          +-------------------+      +-------------------+     +-------------------+
          |   Retrievers      |      |     Graders       |     |    Generator      |
          | (retrievers/)     |      |   (graders/)      |     |  (generator/)     |
          |                   |      |                   |     |                   |
          | VectorRetriever   |      | RelevanceGrader   |     | AnswerGenerator   |
          | WebRetriever      |      | HallucinationGrader|    | ContextBuilder    |
          | GraphRetriever    |      | AnswerGrader      |     | ResponseFormatter |
          | EnsembleRetriever |      | QueryRewriter     |     |                   |
          | BM25Retriever     |      |                   |     |                   |
          +-------------------+      +-------------------+     +-------------------+
                    |
                    v
          +-------------------+
          |   Vector Stores   |
          | (vector_stores/)  |
          |                   |
          | ChromaStore       |
          | FAISSStore        |
          | PineconeStore     |
          +-------------------+
                    ^
                    |
          +-------------------+
          |  LLM Providers    |
          |    (llm/)         |
          |                   |
          | OpenAILLM         |
          | ClaudeLLM         |
          | GroqLLM           |
          | LocalLLM (Ollama) |
          +-------------------+

+------------------------------------------------------------------+
|                    LangGraph Workflows                            |
|  (langgraph_workflows/)                                           |
|                                                                   |
|  AdaptiveWorkflow   SelfRAGWorkflow   CorrectiveRAGWorkflow       |
|  (classify+route+   (retrieve+reflect (retrieve+grade+            |
|   retrieve+grade+    +generate loop)   correct+generate)          |
|   generate+grade+                                                |
|   rewrite loop)      GraphRAGWorkflow                             |
|                      (extract entities +                          |
|                       traverse graph + generate)                  |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|                       Services Layer                              |
|                                                                   |
| +----------------+ +----------------+ +----------------+          |
| |DocumentService | |IndexingService | | CacheService   |          |
| | CRUD for docs  | | Chunk & index  | | In-memory TTL  |          |
| +----------------+ | docs to vector | | cache          |          |
|                    | store          | +----------------+          |
| +----------------+ +----------------+                              |
| |AnalyticsService| | QueryService   |                             |
| | Log & report   | | Simple classify|                             |
| | query stats    | | + route        |                             |
| +----------------+ +----------------+                             |
+------------------------------------------------------------------+
```

---

## Query Flow Pipeline

### Step-by-Step Execution

```
 1. QUERY ARRIVES
    Client POST /api/v1/query { "text": "What is the latest on AI regulation?", "top_k": 5 }
         |
         v
 2. QUERY CLASSIFIER
    QueryClassifier.classify(query) returns ClassificationResult:
    - query_type: "factual" | "exploratory" | "comparative" | "procedural" | "opinion"
    - complexity: "simple" | "moderate" | "complex"
    - needs_docs: bool       — checks for temporal keywords
    - needs_web: bool        — checks for temporal/keyword presence
    - is_time_sensitive: bool
    - needs_graph: bool      — checks for relationship keywords
         |
         v
 3. STRATEGY SELECTOR
    StrategySelector.select(classification) returns strategy name:
    - needs_docs=false && needs_web=false && needs_graph=false  → "direct_llm"
    - needs_docs=true  && needs_web=false                      → "document_rag"
    - needs_docs=false && needs_web=true                       → "web_search_rag"
    - needs_docs=true  && needs_web=true                       → "hybrid_rag"
    - needs_graph=true                                         → "graph_rag"
    - fallback                                                 → "self_rag"
         |
         v
 4. STRATEGY EXECUTION
    strategy.execute(query, top_k=5)
    |
    +-- DirectLLM:      llm.generate(query) — no retrieval
    +-- DocumentRAG:    VectorRetriever.retrieve → llm.generate_with_context
    +-- WebSearchRAG:   WebRetriever.retrieve    → llm.generate_with_context
    +-- HybridRAG:      VectorRetriever + WebRetriever → llm.generate_with_context
    +-- GraphRAG:       GraphRetriever.retrieve  → llm.generate_with_context
    +-- SelfRAG:        loop { retrieve → grade → generate → check }
         |
         v
 5. CONFIDENCE SCORING
    ConfidenceScorer.score(result):
    - Base score from strategy type (direct_llm=0.95, self_rag=0.90, etc.)
    - +0.05 per source (max +0.15)
    - +0.02 per document (max +0.10)
    - ×0.5 if answer contains "error"
    - Final score capped at 1.0
         |
         v
 6. RESPONSE RETURNED
    {
      "query": "...",
      "strategy": "document_rag",
      "answer": "...",
      "sources": [...],
      "confidence": 0.92,
      "latency": 1.234
    }
```

---

## Module Descriptions

### `backend/` — Application Root

| Path | Description |
|------|-------------|
| `main.py` | FastAPI application entry point. Configures CORS, includes router at `/api/v1`, exposes `/health`. |
| `api/routes.py` | All HTTP endpoints: query, document upload/list/delete, strategies list, analytics, health. Lazy-initializes services. |
| `api/schemas.py` | Pydantic models for request/response serialization: `QueryRequest`, `QueryResponse`, `DocumentUploadResponse`, `AnalyticsResponse`. |
| `api/middleware.py` | Request logging middleware — logs method, path, and duration. |
| `api/dependencies.py` | FastAPI dependency injection functions for service instances. |

### `backend/adaptive_rag/router/` — Query Intelligence

| File | Description |
|------|-------------|
| `query_classifier.py` | `QueryClassifier` — keyword-based classification of query type, complexity, and retrieval needs. Returns `ClassificationResult`. |
| `strategy_selector.py` | `StrategySelector` — maps classification to a strategy name using precedence rules. |
| `confidence_scorer.py` | `ConfidenceScorer` — computes a 0.0–1.0 confidence score based on strategy type, source count, and error detection. |
| `query_router.py` | `QueryRouter` — convenience facade combining classifier + selector + scorer. |

### `backend/adaptive_rag/strategies/` — Execution Engines

| File | Description |
|------|-------------|
| `base_strategy.py` | `BaseStrategy` — abstract class with `execute(query)` and `name()`. |
| `direct_llm_strategy.py` | Answers using LLM knowledge alone — no retrieval. Fastest path. |
| `document_rag_strategy.py` | Vector DB retrieval → relevance filtering → context building → generation. |
| `web_search_strategy.py` | DuckDuckGo web search → context → generation. |
| `hybrid_strategy.py` | Combines document retrieval (top-3) + web search (top-2) → merged context → generation. |
| `graph_rag_strategy.py` | Entity extraction → graph-based vector retrieval → generation. |
| `self_rag_strategy.py` | Iterative loop: retrieve → grade relevance → generate → check hallucination → retry. Max 3 iterations. |

### `backend/adaptive_rag/retrievers/` — Information Retrieval

| File | Description |
|------|-------------|
| `base_retriever.py` | `BaseRetriever` — abstract `retrieve(query, top_k)` method. |
| `vector_retriever.py` | Wraps any `BaseVectorStore` with `similarity_search_with_score`. Runs in thread executor for async compatibility. |
| `web_retriever.py` | DuckDuckGo search via `duckduckgo_search` library. Returns title, href, body. |
| `graph_retriever.py` | Extracts named entities from query (uppercase/long words), retrieves related documents from vector store per entity. |
| `ensemble_retriever.py` | Runs multiple retrievers in parallel, deduplicates by source, combines results. |
| `bm25_retriever.py` | Keyword-based BM25 retrieval using `rank_bm25`. Tokenizes corpus, returns scored documents. |

### `backend/adaptive_rag/graders/` — Quality Assurance

| File | Description |
|------|-------------|
| `relevance_grader.py` | Grades document relevance to query. Uses LLM if available, else keyword overlap heuristic. |
| `hallucination_grader.py` | Detects hallucinations by checking answer grounding in context. LLM-based or heuristic word overlap. |
| `answer_grader.py` | Grades answer quality based on length, punctuation, and connective words. |
| `query_rewriter.py` | Rewrites queries for improved retrieval using LLM feedback. |

### `backend/adaptive_rag/generator/` — Answer Synthesis

| File | Description |
|------|-------------|
| `answer_generator.py` | Builds a prompt from query + context and generates an answer via LLM. |
| `context_builder.py` | Joins document contents with double newlines. |
| `response_formatter.py` | Structures final response with answer, sources, and metadata. |

### `backend/adaptive_rag/langgraph_workflows/` — LangGraph State Machines

| File | Description |
|------|-------------|
| `adaptive_workflow.py` | Full workflow: classify → route → retrieve → grade docs → generate → grade answer → (rewrite/web search loop) → format. |
| `self_rag_workflow.py` | Iterative self-reflection loop: retrieve → reflect → generate. Rewrites query based on relevance feedback. |
| `corrective_rag_workflow.py` | Retrieve → grade relevance → correct with web search if low relevance → generate. |
| `graph_rag_workflow.py` | Extract entities → traverse graph for each entity → generate answer from relationship context. |

### `backend/llm/` — LLM Providers

| File | Description |
|------|-------------|
| `llm_factory.py` | `LLMFactory.create(provider)` — returns the appropriate LLM instance by name. |
| `openai_llm.py` | GPT-4 via `langchain_openai.ChatOpenAI`. Methods: `generate`, `generate_with_context`, `grade_relevance`, `grade_answer`, `detect_hallucination`. |
| `claude_llm.py` | Claude 3 Opus via `langchain_anthropic.ChatAnthropic`. Same method interface. |
| `groq_llm.py` | Mixtral 8x7B via `langchain_groq.ChatGroq`. Same method interface. |
| `local_llm.py` | Local models via `langchain_community.Ollama`. Supports Llama 2, Mistral, etc. |

### `backend/vector_stores/` — Vector Databases

| File | Description |
|------|-------------|
| `base_store.py` | Abstract `BaseVectorStore` with `add_documents` and `similarity_search`. |
| `chroma_store.py` | ChromaDB with HuggingFace `all-MiniLM-L6-v2` embeddings. Persistent by default. |
| `faiss_store.py` | FAISS in-memory vector store with same embedding model. |
| `pinecone_store.py` | Pinecone cloud vector store. Requires API key and index name. |

### `backend/document_loaders/` — Document Ingestion

| File | Description |
|------|-------------|
| `pdf_loader.py` | Extracts text from PDF using `pypdf`. |
| `txt_loader.py` | Reads UTF-8 text files. |
| `csv_loader.py` | Parses CSV rows into pipe-delimited text. |
| `docx_loader.py` | Extracts paragraphs and table cells from DOCX using `python-docx`. |
| `url_loader.py` | Placeholder for URL-based loading. |
| `batch_loader.py` | Placeholder for batch document loading. |

### `backend/services/` — Application Services

| File | Description |
|------|-------------|
| `adaptive_rag_service.py` | Central orchestrator: classify → select → execute → score. Registers strategies, handles errors gracefully. |
| `document_service.py` | In-memory document CRUD (upload, list, delete, get). Links to vector store for source-based deletion. |
| `indexing_service.py` | Extracts text via document loaders, chunks with overlap, adds to vector store. |
| `cache_service.py` | Simple in-memory TTL cache with get/set/invalidate/clear. |
| `analytics_service.py` | Logs each query with strategy, latency, confidence. Returns aggregate stats and top queries. |
| `query_service.py` | Lightweight query classification + strategy selection without full execution. |

### `backend/models/` — Data Models

| File | Description |
|------|-------------|
| `query.py` | `QueryRequest` and `QueryResponse` Pydantic models. |
| `rag_response.py` | `RAGResponse` with optional grading metadata. |
| `document.py` | `Document` model for internal document representation. |
| `strategy.py` | `StrategyInfo` with name, description, speed, use_case. |
| `retrieval_result.py` | `RetrievalResult` with content, score, source. |
| `database.py` | SQLAlchemy async engine and session manager. |

### `backend/utils/` — Utilities

| File | Description |
|------|-------------|
| `config.py` | `Settings` class using `pydantic-settings`. Loads from `.env` file. All config values have defaults. |
| `logger.py` | `setup_logger` — configures stream handler with timestamp format. |
| `exceptions.py` | `RAGException` hierarchy: `RetrievalException`, `GenerationException`, `ConfigurationException`. |
| `validators.py` | `validate_query` (non-empty check) and `validate_file_extension` (pdf/docx/txt/csv). |
| `helpers.py` | `timed` decorator for async function timing; `chunk_text` utility. |

---

## How LangGraph Workflows Fit In

LangGraph workflows live in `langgraph_workflows/` and provide state-machine orchestration for complex multi-step RAG processes. They are **complementary** to the simpler strategy-based execution in `strategies/`.

**Relationship to Strategies:**

- The `strategies/` module provides self-contained `execute()` methods — call a strategy, get a result. These are used by `AdaptiveRAGService` for the primary query path.
- The `langgraph_workflows/` module implements the same logical patterns using LangGraph's `StateGraph`, which adds explicit state management, conditional edges, and multi-node execution graphs.

**When LangGraph is used:**

| Workflow | Purpose | Key Difference from Strategy |
|----------|---------|------------------------------|
| `AdaptiveWorkflow` | Full pipeline with classification, routing, retrieval, grading, rewriting, and web search loops | Has dedicated nodes for `rewrite_query` and `web_search` with max-iteration guards |
| `SelfRAGWorkflow` | Iterative retrieve-reflect-generate with query rewriting | Tracks reflection notes per iteration, rewrites query based on relevance feedback |
| `CorrectiveRAGWorkflow` | Retrieve → grade → correct with web fallback | Automatically supplements low-relevance docs with web results |
| `GraphRAGWorkflow` | Entity extraction → graph traversal → generation | Explicit entity extraction and per-entity graph traversal as separate nodes |

All workflows implement a `run(query)` async method that returns a structured result dictionary.

---

## Configuration Management

Configuration is managed via `pydantic-settings` in `backend/utils/config.py`:

```python
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
```

Settings are loaded from `.env` file at application startup. The `settings` singleton is imported application-wide. All values have sensible defaults, making the system runnable with minimal configuration (only API keys for chosen LLM provider are required).

See `.env.example` for the full list of configurable environment variables.
