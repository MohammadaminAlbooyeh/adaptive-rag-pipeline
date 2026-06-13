# Architecture

## Overview

The Adaptive RAG Pipeline uses a modular architecture with:

- **Query Router**: Classifies and routes queries
- **Strategies**: Pluggable RAG strategies
- **Retrievers**: Multiple retrieval backends
- **Graders**: Quality assurance components
- **LangGraph Workflows**: Stateful orchestration
