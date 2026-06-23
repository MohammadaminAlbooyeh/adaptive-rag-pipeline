# API Reference

## Base URL

All API endpoints are served at `http://localhost:8000` (development) or your deployed domain.

API routes are prefixed with `/api/v1`. Health check is at root level.

---

## Authentication

The current version does not implement authentication. CORS is configured to allow all origins. In production, add authentication middleware and restrict CORS origins.

---

## Endpoints

### POST /api/v1/query

Submit a natural language query to the Adaptive RAG Pipeline. This is the primary endpoint — it classifies the query, selects the optimal strategy, retrieves context, generates an answer, and scores confidence.

#### Request Body

```json
{
  "text": "What is the latest on AI regulation?",
  "strategy": null,
  "top_k": 5
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | **Yes** | — | The natural language query |
| `strategy` | string or null | No | `null` | Force a specific strategy. If null, auto-selected. See "Available Strategies" below. |
| `top_k` | integer | No | `5` | Number of documents/web results to retrieve |

#### Available Strategy Values

| Value | Description |
|-------|-------------|
| `"direct_llm"` | Answer directly from LLM knowledge |
| `"document_rag"` | Retrieve from uploaded documents |
| `"web_search_rag"` | Search the web for fresh information |
| `"hybrid_rag"` | Combine document and web search |
| `"graph_rag"` | Use knowledge graph relationships |
| `"self_rag"` | Iterative retrieval with self-reflection |

#### Success Response (200)

```json
{
  "query": "What is the latest on AI regulation?",
  "strategy": "web_search_rag",
  "answer": "Recent AI regulation developments include the EU AI Act...",
  "sources": [
    {
      "content": "The European Parliament approved the AI Act...",
      "source": "https://example.com/ai-regulation",
      "score": 0.8
    }
  ],
  "confidence": 0.82,
  "latency": 2.341
}
```

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | The original query text |
| `strategy` | string | The strategy used to generate the answer |
| `answer` | string | The generated answer text |
| `sources` | array | List of source documents (varies by strategy) |
| `confidence` | float | Confidence score 0.0–1.0 |
| `latency` | float | Total processing time in seconds |

#### Source Object (varies by strategy)

For `document_rag`:
```json
{
  "content": "Document text content...",
  "source": "filename.pdf",
  "score": 0.85
}
```

For `web_search_rag`:
```json
{
  "content": "Web page snippet...",
  "source": "https://example.com/article",
  "score": 0.8
}
```

For `hybrid_rag` (content truncated to 100 chars):
```json
{
  "content": "First 100 characters of the document...",
  "source": "filename.pdf",
  "score": 0.85
}
```

For `graph_rag` (content truncated to 100 chars):
```json
{
  "content": "First 100 characters...",
  "source": "Graph",
  "score": 0.7
}
```

#### Error Response (500)

```json
{
  "detail": "Strategy 'nonexistent' not found"
}
```

#### Examples

**Simple factual query (auto-selects direct_llm):**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the capital of France?"}'
```

**Time-sensitive query with forced web search:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"text": "Latest stock market news today", "strategy": "web_search_rag", "top_k": 3}'
```

**Document-specific query:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What does the contract say about termination?"}'
```

---

### POST /api/v1/documents/upload

Upload a document to be indexed into the vector store. The document is parsed, chunked, and embedded for retrieval.

#### Request

Multipart form-data with a single file field.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | **Yes** | The document file to upload |

#### Supported Formats

| Format | Extension | Loader | Notes |
|--------|-----------|--------|-------|
| PDF | `.pdf` | `PDFLoader` | Uses `pypdf`, extracts text per page |
| Plain Text | `.txt` | `TXTLoader` | UTF-8 encoding |
| CSV | `.csv` | `CSVLoader` | Rows joined with `\|`, lines joined with `\n` |
| Word | `.docx` | `DOCXLoader` | Extracts paragraphs and table cells |

File extensions are validated. Unsupported formats return a 500 error.

#### Indexing Process

1. File is read into memory
2. Appropriate loader extracts text based on file extension
3. Text is chunked into segments of ~500 characters with 50-character overlap
4. Each chunk is embedded using HuggingFace `all-MiniLM-L6-v2`
5. Embeddings + metadata (source filename, doc_id, chunk_index) are stored in the vector store

#### Success Response (200)

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "report.pdf",
  "status": "indexed"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | UUID assigned to the document |
| `filename` | string | Original filename |
| `status` | string | Always `"indexed"` on success |

#### Error Response (500)

```json
{
  "detail": "Failed to index document: Unsupported file format"
}
```

#### Example

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@report.pdf"
```

---

### GET /api/v1/documents

List all uploaded documents with metadata.

#### Success Response (200)

```json
{
  "documents": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "filename": "report.pdf",
      "uploaded_at": "2025-01-15T10:30:00",
      "size": 1024000,
      "status": "uploaded"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `documents` | array | List of document metadata objects |
| `documents[].id` | string | Document UUID |
| `documents[].filename` | string | Original filename |
| `documents[].uploaded_at` | string | ISO 8601 timestamp of upload |
| `documents[].size` | integer | File size in bytes |
| `documents[].status` | string | Upload status |

Document metadata is stored in-memory and is lost on server restart. In production, use PostgreSQL persistence configured via `DATABASE_URL`.

#### Example

```bash
curl http://localhost:8000/api/v1/documents
```

---

### DELETE /api/v1/documents/{doc_id}

Delete a document and remove its chunks from the vector store.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `doc_id` | string | **Yes** | UUID of the document to delete |

#### Success Response (200)

```json
{
  "status": "deleted"
}
```

#### Error Response (500)

```json
{
  "detail": "Document not found"
}
```

#### Example

```bash
curl -X DELETE http://localhost:8000/api/v1/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

### GET /api/v1/strategies

List all available RAG strategies with descriptions.

#### Success Response (200)

```json
{
  "strategies": [
    {
      "name": "direct_llm",
      "description": "Answer directly using LLM knowledge without retrieval"
    },
    {
      "name": "document_rag",
      "description": "Retrieve relevant documents and generate answer"
    },
    {
      "name": "web_search_rag",
      "description": "Search the web for relevant information"
    },
    {
      "name": "hybrid_rag",
      "description": "Combine document and web search retrieval"
    },
    {
      "name": "graph_rag",
      "description": "Retrieve using knowledge graph relationships"
    },
    {
      "name": "self_rag",
      "description": "Retrieve, critique, and regenerate answers"
    }
  ]
}
```

#### Example

```bash
curl http://localhost:8000/api/v1/strategies
```

---

### GET /api/v1/analytics

Retrieve aggregate query statistics for the current session. Analytics are maintained in-memory and reset on server restart.

#### Success Response (200)

```json
{
  "total_queries": 42,
  "avg_latency": 1.234,
  "avg_confidence": 0.85,
  "success_rate": 0.95,
  "strategy_distribution": {
    "direct_llm": 10,
    "document_rag": 15,
    "web_search_rag": 8,
    "hybrid_rag": 5,
    "graph_rag": 2,
    "self_rag": 2
  },
  "top_queries": [
    {"query": "What is AI?", "count": 5},
    {"query": "Latest news", "count": 3}
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `total_queries` | integer | Total queries processed |
| `avg_latency` | float | Average response time in seconds |
| `avg_confidence` | float | Average confidence score (0.0–1.0) |
| `success_rate` | float | Fraction of queries with confidence > 0.5 |
| `strategy_distribution` | object | Count of queries per strategy name |
| `top_queries` | array | Top 10 most frequent queries with counts |

#### Example

```bash
curl http://localhost:8000/api/v1/analytics
```

---

### GET /health

Simple health check endpoint (not under `/api/v1` prefix).

#### Success Response (200)

```json
{
  "status": "healthy",
  "service": "Adaptive RAG Pipeline"
}
```

#### Example

```bash
curl http://localhost:8000/health
```

---

## Error Response Format

All errors return an HTTP 500 status with a JSON body:

```json
{
  "detail": "Descriptive error message"
}
```

Common error scenarios:

| Scenario | HTTP Status | Detail Message |
|----------|-------------|----------------|
| Strategy not found | 500 | `Strategy '<name>' not implemented` |
| Document upload failure | 500 | `Failed to index document: ...` |
| Retrieval failure | 500 | `Error processing query: ...` |
| Missing query text | 500 | Pydantic validation error (422) |

---

## Rate Limiting

The current version does not implement rate limiting. For production deployments, add rate limiting via:

- **FastAPI middleware** (e.g., `slowapi`)
- **Reverse proxy** (e.g., Nginx `limit_req_zone`)
- **API Gateway** (e.g., Kong, AWS API Gateway)

Recommended limits: 60 requests per minute per IP for `/api/v1/query`, 10 requests per minute for `/api/v1/documents/upload`.

---

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Both are auto-generated by FastAPI from the Pydantic schemas.
