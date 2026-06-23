# Adaptive RAG Pipeline — Documentation

## Overview

The Adaptive RAG Pipeline is a modular, strategy-driven Retrieval-Augmented Generation system that intelligently classifies queries, selects the optimal retrieval strategy, generates grounded answers, and scores confidence — all through a single API endpoint.

## Documentation Index

| Document | Description |
|----------|-------------|
| [**ARCHITECTURE.md**](ARCHITECTURE.md) | System architecture, component diagram, query flow pipeline, module descriptions, and configuration management. |
| [**STRATEGIES.md**](STRATEGIES.md) | All 6 RAG strategies (DirectLLM, DocumentRAG, WebSearchRAG, HybridRAG, GraphRAG, SelfRAG) with use cases, flow diagrams, implementation details, and comparison table. |
| [**API_REFERENCE.md**](API_REFERENCE.md) | Complete API reference with request/response schemas, examples, error formats, and rate limiting notes for all endpoints. |
| [**LANGGRAPH_WORKFLOW.md**](LANGGRAPH_WORKFLOW.md) | LangGraph state machine workflows — AdaptiveWorkflow, SelfRAGWorkflow, CorrectiveRAGWorkflow, and GraphRAGWorkflow — with state diagrams, node descriptions, and decision functions. |
| [**DEPLOYMENT.md**](DEPLOYMENT.md) | Deployment guide covering local setup, Docker Compose, environment variables, production considerations, and CI/CD pipeline. |

## Additional Resources

- **Getting Started**: [`GETTING_STARTED.md`](../GETTING_STARTED.md) — fast-start guide
- **Examples**: [`examples/`](../examples/) — runnable Python example scripts
- **Tests**: [`tests/`](../tests/) — unit and integration tests
- **OpenAPI Docs**: `http://localhost:8000/docs` (Swagger) or `http://localhost:8000/redoc` (ReDoc)

## Project Structure

```
backend/
  main.py                   # FastAPI entry point
  api/                       # API layer (routes, schemas, middleware)
  adaptive_rag/              # Core RAG engine
    router/                   # Classification, selection, scoring
    strategies/               # 6 RAG strategies
    retrievers/               # 5 retriever implementations
    graders/                  # Relevance, hallucination, answer grading
    generator/                # Answer synthesis
    langgraph_workflows/      # LangGraph state machines
  services/                  # Application orchestration
  llm/                       # LLM providers (OpenAI, Claude, Groq, Local)
  vector_stores/             # ChromaDB, FAISS, Pinecone
  document_loaders/          # PDF, TXT, CSV, DOCX, URL, Batch
  models/                    # Pydantic data models
  utils/                     # Config, logger, exceptions, validators
```

## Quick Start

```bash
cp .env.example .env          # Add your API keys
pip install -r requirements.txt
uvicorn backend.main:app --reload
curl http://localhost:8000/health
```
