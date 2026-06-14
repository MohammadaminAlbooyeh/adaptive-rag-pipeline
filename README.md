# adaptive-rag-pipeline

An intelligent RAG system that **analyzes each query** and **automatically selects the best retrieval strategy** — powered by LangChain, LangGraph, FastAPI, and React.

## ✨ Features

- **🎯 Adaptive Strategy Selection**: Classifies queries and routes to the optimal RAG strategy
- **🔄 6 RAG Strategies**: Direct LLM, Document RAG, Web Search RAG, Hybrid RAG, Graph RAG, Self-RAG
- **📊 Query Classification**: Analyzes query type, complexity, temporal sensitivity
- **📚 Document Management**: Upload, index, and retrieve from PDF, DOCX, TXT, CSV
- **🌐 Web Search Integration**: Real-time information retrieval via DuckDuckGo
- **⚡ Confidence Scoring**: Automatic grading of retrieval and answer quality
- **📈 Analytics Dashboard**: Track queries, strategies, latency, and success rates
- **💾 Query History**: Automatic tracking and replay of previous queries
- **🚀 FastAPI Backend**: High-performance REST API
- **⚛️ React Frontend**: Modern, responsive UI with real-time updates

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo>
cd adaptive-rag-pipeline
cp .env.example .env
# Edit .env with your API keys

# 2. Option A: Docker
docker-compose up

# 2. Option B: Local
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
make run  # Terminal 1: Backend
cd frontend && npm install && npm start  # Terminal 2: Frontend
```

Open `http://localhost:3000` and start querying!

## Project Structure

```text
adaptive-rag-pipeline/
│
├── 📱 Frontend (React)
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # React hooks
│   │   ├── services/          # API integration
│   │   └── App.js
│   └── public/                # Static assets
│
├── 🧠 Backend (FastAPI)
│   ├── main.py                # FastAPI application
│   │
│   ├── api/                   # REST API Layer
│   │   ├── routes.py          # API endpoints
│   │   ├── schemas.py         # Request/response models
│   │   ├── dependencies.py    # Dependency injection
│   │   └── middleware.py      # HTTP middleware
│   │
│   ├── adaptive_rag/          # Core RAG Logic
│   │   ├── router/            # Query routing
│   │   ├── strategies/        # RAG strategies (6 types)
│   │   ├── langgraph_workflows/  # LangGraph state machines
│   │   ├── retrievers/        # Retrieval implementations
│   │   ├── graders/           # Quality scoring
│   │   └── generator/         # Response generation
│   │
│   ├── services/              # Business Logic
│   │   ├── adaptive_rag_service.py
│   │   ├── query_service.py
│   │   ├── document_service.py
│   │   ├── indexing_service.py
│   │   ├── cache_service.py
│   │   └── analytics_service.py
│   │
│   ├── vector_stores/         # Vector Databases
│   │   ├── base_store.py
│   │   ├── chroma_store.py
│   │   ├── faiss_store.py
│   │   └── pinecone_store.py
│   │
│   ├── document_loaders/      # File Format Support
│   │   ├── pdf_loader.py
│   │   ├── docx_loader.py
│   │   ├── csv_loader.py
│   │   ├── txt_loader.py
│   │   ├── url_loader.py
│   │   └── batch_loader.py
│   │
│   ├── llm/                   # LLM Integrations
│   │   ├── claude_llm.py      # Anthropic Claude
│   │   ├── openai_llm.py      # OpenAI GPT
│   │   ├── groq_llm.py        # Groq LLaMA
│   │   ├── local_llm.py       # Local models
│   │   └── llm_factory.py
│   │
│   ├── models/                # Data Models
│   │   ├── database.py
│   │   ├── document.py
│   │   ├── query.py
│   │   ├── rag_response.py
│   │   └── strategy.py
│   │
│   ├── langchain_components/  # LangChain Components
│   │   ├── chains/
│   │   ├── embeddings/
│   │   └── prompts/
│   │
│   └── utils/                 # Utilities
│       ├── config.py
│       ├── logger.py
│       ├── exceptions.py
│       └── validators.py
│
├── 📚 Documentation
│   ├── ARCHITECTURE.md        # Detailed architecture
│   ├── STRATEGIES.md          # RAG strategies explained
│   ├── LANGGRAPH_WORKFLOW.md  # Workflow documentation
│   ├── API_REFERENCE.md       # API endpoints
│   └── DEPLOYMENT.md          # Deployment guide
│
├── 📓 Notebooks
│   ├── 01_Adaptive_RAG_Introduction.ipynb
│   ├── 02_Query_Classification.ipynb
│   ├── 03_Strategy_Selection.ipynb
│   ├── 04_Document_RAG.ipynb
│   ├── 05_Web_Search_RAG.ipynb
│   ├── 06_Hybrid_RAG.ipynb
│   ├── 07_Self_RAG_Workflow.ipynb
│   ├── 08_Corrective_RAG.ipynb
│   ├── 09_LangGraph_Workflow.ipynb
│   └── 10_Real_World_Examples.ipynb
│
├── 🧪 Tests
│   ├── unit/                  # Unit tests
│   │   ├── test_query_classifier.py
│   │   ├── test_strategy_selector.py
│   │   ├── test_retrievers.py
│   │   └── ...
│   └── integration/           # Integration tests
│       ├── test_adaptive_workflow.py
│       ├── test_corrective_rag.py
│       └── ...
│
├── 💡 Examples
│   ├── basic_adaptive_rag.py
│   ├── document_qa_example.py
│   ├── hybrid_rag_example.py
│   └── web_search_example.py
│
├── docker-compose.yml         # Docker setup
├── Dockerfile
├── requirements.txt           # Python dependencies
├── Makefile                   # Build commands
└── LICENSE
```

### Complete End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React)                               │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │   Query Page     │  │  Documents Page  │  │  Analytics Page  │      │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘      │
│           │                     │                     │                 │
│           ├─────────────────────┼─────────────────────┤                 │
│           │                     │                     │                 │
│        useAdaptiveRAG       useDocuments          useAnalytics          │
│           │                     │                     │                 │
└───────────┼─────────────────────┼─────────────────────┼─────────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   API SERVICE LAYER (FastAPI)                           │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │  POST /api/v1/query                                          │       │
│  │  GET  /api/v1/documents, /api/v1/strategies                 │       │
│  │  POST /api/v1/documents/upload                              │       │
│  │  DELETE /api/v1/documents/{doc_id}                          │       │
│  │  GET /api/v1/analytics                                      │       │
│  └──────────────────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
┌──────────────────────────┐  ┌────────────────────────────┐  ┌─────────┐
│  ADAPTIVE RAG SERVICE    │  │  DOCUMENT SERVICE          │  │ANALYTICS│
├──────────────────────────┤  ├────────────────────────────┤  ├─────────┤
│ • Query Processing       │  │ • Upload Management        │  │ • Logging│
│ • Strategy Registration  │  │ • Document CRUD            │  │ • Stats  │
│ • Confidence Scoring     │  │ • Metadata Tracking        │  │ • Metrics│
└──────────┬───────────────┘  └────────┬───────────────────┘  └────┬────┘
           │                           │                           │
           │              ┌────────────┼──────────────┐             │
           │              │                           │             │
           ▼              ▼                           ▼             │
    ┌──────────────────────────────────────────────────────────┐   │
    │           INDEXING SERVICE                               │   │
    ├──────────────────────────────────────────────────────────┤   │
    │  ┌─────────────────────────────────────────────────┐     │   │
    │  │  Document Loaders                               │     │   │
    │  │  • PDF Loader      • TXT Loader                 │     │   │
    │  │  • DOCX Loader     • CSV Loader                 │     │   │
    │  └─────────────────────────────────────────────────┘     │   │
    │                      │                                   │   │
    │                      ▼                                   │   │
    │  ┌─────────────────────────────────────────────────┐     │   │
    │  │  Chunking & Embedding                           │     │   │
    │  │  • Text Splitting (500 char chunks)             │     │   │
    │  │  • Overlap Management                           │     │   │
    │  └─────────────────────────────────────────────────┘     │   │
    │                      │                                   │   │
    └──────────────────────┼───────────────────────────────────┘   │
                           │                                       │
        ┌──────────────────┼──────────────────┐                   │
        │                  │                  │                   │
        ▼                  ▼                  ▼                   │
   ┌────────────┐  ┌──────────────┐  ┌──────────────────┐        │
   │QUERY CLASS │  │ STRATEGY     │  │ VECTOR RETRIEVAL │        │
   │IFIER       │  │ SELECTOR     │  │                  │        │
   ├────────────┤  ├──────────────┤  ├──────────────────┤        │
   │ • Type     │  │ • Routes to  │  │ • Similarity     │        │
   │ • Complex. │  │   optimal    │  │   Search         │        │
   │ • Temporal │  │   strategy   │  │ • Relevance      │        │
   │ • Domain   │  │ • Confidence │  │   Scoring        │        │
   └─────┬──────┘  │   Scoring    │  └────────┬─────────┘        │
         │         └──────┬───────┘           │                  │
         └─────────┬──────┴───────┬───────────┘                  │
                   │              │                              │
                   ▼              ▼                              │
    ┌──────────────────────────────────────────────────────┐    │
    │         6 RAG STRATEGIES                              │    │
    ├──────────────────────────────────────────────────────┤    │
    │                                                       │    │
    │  ┌──────────────────┐    ┌──────────────────┐       │    │
    │  │ DIRECT LLM       │    │ DOCUMENT RAG     │       │    │
    │  ├──────────────────┤    ├──────────────────┤       │    │
    │  │ • No retrieval   │    │ • Vector search  │       │    │
    │  │ • Pure knowledge │    │ • Context build  │       │    │
    │  │ • Fast response  │    │ • LLM generation │       │    │
    │  └──────────────────┘    └──────────────────┘       │    │
    │                                                       │    │
    │  ┌──────────────────┐    ┌──────────────────┐       │    │
    │  │ WEB SEARCH RAG   │    │ HYBRID RAG       │       │    │
    │  ├──────────────────┤    ├──────────────────┤       │    │
    │  │ • DuckDuckGo API │    │ • Doc + Web      │       │    │
    │  │ • Fresh info     │    │ • Combined ctx   │       │    │
    │  │ • Current events │    │ • Best of both   │       │    │
    │  └──────────────────┘    └──────────────────┘       │    │
    │                                                       │    │
    │  ┌──────────────────┐    ┌──────────────────┐       │    │
    │  │ GRAPH RAG        │    │ SELF-RAG         │       │    │
    │  ├──────────────────┤    ├──────────────────┤       │    │
    │  │ • Entity extract │    │ • Retrieve docs  │       │    │
    │  │ • Relationships  │    │ • Grade relevance│       │    │
    │  │ • Knowledge graph│    │ • Generate ans.  │       │    │
    │  └──────────────────┘    │ • Check grounds  │       │    │
    │                          │ • Iterate if bad │       │    │
    │                          └──────────────────┘       │    │
    └────────────────┬─────────────────────────────────────┘    │
                     │                                           │
         ┌───────────┼───────────┐                              │
         │           │           │                              │
         ▼           ▼           ▼                              │
   ┌──────────┐ ┌─────────┐ ┌────────────┐                    │
   │ VECTOR   │ │ WEB     │ │ GRAPH      │                    │
   │RETRIEVER │ │RETRIEVER│ │RETRIEVER   │                    │
   └────┬─────┘ └────┬────┘ └─────┬──────┘                    │
        │            │            │                           │
        └────────────┼────────────┘                           │
                     │                                        │
                     ▼                                        │
         ┌───────────────────────┐                           │
         │  VECTOR STORE LAYER   │                           │
         ├───────────────────────┤                           │
         │ • Chroma (default)    │                           │
         │ • FAISS               │                           │
         │ • Pinecone            │                           │
         └───────────┬───────────┘                           │
                     │                                        │
         ┌───────────┴───────────┐                           │
         │                       │                           │
         ▼                       ▼                           │
    ┌─────────────┐      ┌──────────────┐                  │
    │EMBEDDINGS   │      │LLM SELECTION │                  │
    ├─────────────┤      ├──────────────┤                  │
    │ • HF Models │      │ • Claude     │                  │
    │ • OpenAI    │      │ • OpenAI     │                  │
    │ • Sentence  │      │ • Groq       │                  │
    │   Transform │      │ • Local      │                  │
    └─────┬───────┘      └──────┬───────┘                  │
          │                     │                          │
          └─────────────┬───────┘                          │
                        │                                  │
                        ▼                                  │
          ┌──────────────────────────────┐               │
          │ CONTEXT BUILDING + GRADING   │               │
          ├──────────────────────────────┤               │
          │ • Relevance Grader           │               │
          │ • Answer Grader              │               │
          │ • Hallucination Grader       │               │
          │ • Query Rewriter             │               │
          └──────────────┬───────────────┘               │
                         │                              │
                         ▼                              │
          ┌──────────────────────────────┐              │
          │ LLM GENERATION               │              │
          ├──────────────────────────────┤              │
          │ • System Prompt              │              │
          │ • Context Injection          │              │
          │ • Response Formatting        │              │
          └──────────────┬───────────────┘              │
                         │                             │
                         ▼                             │
          ┌──────────────────────────────┐             │
          │ CONFIDENCE SCORING           │             │
          ├──────────────────────────────┤             │
          │ • Base Score (by strategy)   │             │
          │ • Source Bonus               │             │
          │ • Document Bonus             │             │
          │ • Error Penalty              │             │
          └──────────────┬───────────────┘             │
                         │                            │
                         └────────────────┬───────────┘
                                          │
                                          ▼
                         ┌────────────────────────────┐
                         │ ANALYTICS LOGGING          │
                         ├────────────────────────────┤
                         │ • Query tracking           │
                         │ • Strategy distribution    │
                         │ • Latency metrics          │
                         │ • Confidence scores        │
                         └────────────┬───────────────┘
                                      │
                                      ▼
                         ┌────────────────────────────┐
                         │ RESPONSE ASSEMBLY          │
                         ├────────────────────────────┤
                         │ • Query                    │
                         │ • Answer                   │
                         │ • Sources                  │
                         │ • Confidence               │
                         │ • Latency                  │
                         │ • Classification           │
                         └────────────┬───────────────┘
                                      │
                                      ▼
                         ┌────────────────────────────┐
                         │ FRONTEND RESPONSE          │
                         ├────────────────────────────┤
                         │ • Display Answer           │
                         │ • Show Sources             │
                         │ • Strategy Badge           │
                         │ • Confidence Bar           │
                         │ • Timing Info              │
                         │ • Save to History          │
                         └────────────────────────────┘
```

### Component Details

**Query Classification:**
- Analyzes query characteristics (factual, exploratory, comparative, procedural, opinion)
- Determines complexity level (simple, moderate, complex)
- Identifies if web search, document retrieval, or graph knowledge needed
- Flags time-sensitive queries

**Strategy Selection:**
- Routes based on classification results
- Direct LLM → No docs/web needed
- Document RAG → Docs needed, no web
- Web Search → Web needed, no docs
- Hybrid RAG → Both docs and web needed
- Graph RAG → Entity relationships needed
- Self-RAG → Iterative retrieval-critique loop

**Retrieval Layer:**
- Vector Retriever: Semantic similarity search via embeddings
- Web Retriever: Real-time search via DuckDuckGo API
- Graph Retriever: Entity-based document retrieval
- Ensemble: Combines multiple retrievers

**Grading System:**
- Relevance Grader: Is document relevant to query?
- Answer Grader: Does answer address query?
- Hallucination Grader: Is answer grounded in context?
- Query Rewriter: Generate alternative queries if needed

**LLM Integration:**
- Claude: Primary LLM (anthropic)
- OpenAI: Alternative (gpt-4)
- Groq: Fast inference (mixtral)
- Local: Self-hosted models

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed technical documentation.
