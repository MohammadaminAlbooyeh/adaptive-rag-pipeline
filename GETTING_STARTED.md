# Getting Started with Adaptive RAG Pipeline

This guide will help you set up and start using the Adaptive RAG Pipeline.

## Prerequisites

- Python 3.9+
- Node.js 16+
- Docker (optional, for containerized setup)
- An API key for Claude AI or OpenAI

## 1. Clone the Repository

```bash
git clone <repository-url>
cd adaptive-rag-pipeline
```

## 2. Set Up Environment Variables

Copy the example environment file and update it with your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key (optional)
ANTHROPIC_MODEL=claude-3-opus-20240229
```

## 3. Backend Setup

### Option A: Local Python Setup

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
make run
# or: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option B: Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up
```

The backend will be available at `http://localhost:8000`

## 4. Frontend Setup

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at `http://localhost:3000`

## 5. Quick Test

1. Open `http://localhost:3000` in your browser
2. Go to the "Query" page
3. Try asking a simple question like "What is machine learning?"
4. The system will automatically select the best strategy and return an answer

## Core Features

### Query Processing

1. **Query Classification**: Automatically categorizes queries (factual, exploratory, comparative, etc.)
2. **Strategy Selection**: Routes to the optimal RAG strategy based on query type
3. **Response Generation**: Generates answers with confidence scores

### RAG Strategies

The system automatically selects one of 6 strategies:

- **Direct LLM**: Uses LLM knowledge without retrieval
- **Document RAG**: Retrieves from uploaded documents
- **Web Search RAG**: Searches the web for information
- **Hybrid RAG**: Combines documents and web search
- **Graph RAG**: Uses entity-based retrieval
- **Self-RAG**: Iterative retrieval and grading

### Document Management

1. Go to "Documents" page
2. Upload PDF, DOCX, TXT, or CSV files
3. Documents are automatically chunked and indexed
4. Retrieved documents appear in answers

### Query History

- Automatically tracks all queries
- Stores strategy selection and confidence scores
- View and replay previous queries from History page

### Analytics

- View query statistics and performance metrics
- Track strategy usage distribution
- Monitor response latency and confidence scores

## API Endpoints

### Query Endpoint
```bash
POST /api/v1/query
Content-Type: application/json

{
  "text": "Your question here",
  "top_k": 5
}
```

### Document Upload
```bash
POST /api/v1/documents/upload
Content-Type: multipart/form-data

file: <your_file>
```

### Get Documents
```bash
GET /api/v1/documents
```

### Delete Document
```bash
DELETE /api/v1/documents/{doc_id}
```

### Get Analytics
```bash
GET /api/v1/analytics
```

### List Strategies
```bash
GET /api/v1/strategies
```

## Configuration

### Vector Store

Default is Chroma (local). Modify in `.env`:

```env
VECTOR_STORE_TYPE=chroma  # or pinecone, faiss
CHROMA_PERSIST_DIR=./chromadb
```

### Embedding Model

```env
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_PROVIDER=openai  # or others
```

### LLM Model

```env
ANTHROPIC_MODEL=claude-3-opus-20240229
OPENAI_MODEL=gpt-4
GROQ_MODEL=mixtral-8x7b-32768
```

## Troubleshooting

### Backend Won't Start

1. Check Python version: `python --version` (should be 3.9+)
2. Verify dependencies: `pip list | grep -i langchain`
3. Check API keys in `.env`
4. Look at logs for specific errors

### Frontend Won't Connect

1. Ensure backend is running on port 8000
2. Check CORS settings in `backend/main.py`
3. Verify API endpoint in `frontend/src/services/api.js`

### Out of Memory

- Reduce chunk size in `IndexingService`
- Use FAISS instead of Chroma for large datasets
- Limit `top_k` in queries

### Slow Responses

1. Check vector store size (rebuild if needed)
2. Reduce embedding model complexity
3. Use faster LLM model (Sonnet vs Opus)
4. Enable caching in `CacheService`

## Development

### Running Tests

```bash
pytest tests/ -v
pytest tests/unit/ -v --cov=backend
```

### Code Quality

```bash
make lint
make format
```

### Database

The system uses Chroma by default (embedded). To use PostgreSQL:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/ragdb
```

## Performance Tips

1. **Batch Document Uploads**: Process multiple documents together
2. **Optimize Chunk Size**: Larger chunks (1000+) for better context, smaller for speed
3. **Cache Results**: Enable Redis caching for frequent queries
4. **Use Web Search Sparingly**: Only for time-sensitive queries
5. **Monitor Confidence Scores**: Retrigger with Self-RAG if low

## Next Steps

- Upload your documents to the Documents page
- Try different query types to see strategy selection
- Check Analytics to understand system performance
- Review the Architecture documentation for technical details

## Support & Documentation

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Strategy Guide](docs/STRATEGIES.md)

## Common Tasks

### Change LLM Provider

1. Update `.env` with new API key
2. Modify `_initialize_services()` in `backend/api/routes.py`
3. Restart backend

### Add Custom Vector Store

1. Create new class in `backend/vector_stores/`
2. Inherit from `BaseVectorStore`
3. Implement required methods
4. Update imports in `routes.py`

### Extend Retrieval Strategies

1. Create new strategy in `backend/adaptive_rag/strategies/`
2. Inherit from `BaseStrategy`
3. Implement `execute()` method
4. Register in `_initialize_services()`

Happy querying! 🚀
