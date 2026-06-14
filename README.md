# adaptive-rag-pipeline

An intelligent RAG system that **analyzes each query** and **automatically selects the best retrieval strategy** — powered by LangChain, LangGraph, and multiple retrieval backends.

## Features

- **Adaptive Strategy Selection**: Classifies each query and routes to the optimal RAG strategy
- **6 RAG Strategies**: Direct LLM, Document RAG, Web Search RAG, Hybrid RAG, Graph RAG, Self-RAG
- **LangGraph Workflows**: Stateful, conditional workflows with retry loops
- **Multiple Retrievers**: Vector search, BM25, web search, ensemble, graph retrieval
- **Confidence Scoring**: Grades retrieval quality and answer correctness
- **FastAPI Backend**: Production-ready REST API
- **React Frontend**: Modern UI with strategy visualization

## Quick Start

```bash
cp .env.example .env
docker-compose up
```

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

## Architecture Flow

```text
User Query (Frontend)
    ↓
FastAPI Gateway
    ↓
Query Classifier → Strategy Selector
    ↓
┌─────────────────────────────────────────────┐
│  6 RAG Strategies                           │
│  ┌──────────────┐  ┌──────────────┐         │
│  │ Direct LLM   │  │ Document RAG │         │
│  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐         │
│  │ Web Search   │  │ Hybrid RAG   │         │
│  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐         │
│  │ Graph RAG    │  │ Self-RAG     │         │
│  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────┘
    ↓
Retrievers (Vector, BM25, Web, Graph, Ensemble)
    ↓
Vector Stores (Chroma, FAISS, Pinecone)
    ↓
LLM Generation + Grading
    ↓
Response with Confidence Scores
    ↓
Frontend Display
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed technical documentation.
