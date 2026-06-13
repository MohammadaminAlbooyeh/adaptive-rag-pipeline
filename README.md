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

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.
