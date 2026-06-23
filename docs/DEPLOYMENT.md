# Deployment Guide

## Prerequisites

| Dependency | Version | Purpose |
|-----------|---------|---------|
| Python | 3.9+ | Runtime for the FastAPI backend |
| pip | 21+ | Python package management |
| Node.js | 16+ | Frontend (if using the React frontend) |
| Docker | 24+ | Containerized deployment |
| Docker Compose | 2.20+ | Multi-service orchestration |

Optional:
- **Ollama** (for LocalLLM support): `brew install ollama` (macOS) or `curl -fsSL https://ollama.com/install.sh | sh`
- **PostgreSQL** 16 (for production persistence)
- **Redis** 7 (for caching layer)

---

## Local Development Setup

### 1. Clone and Configure

```bash
git clone <repository-url>
cd adaptive-rag-pipeline
cp .env.example .env
```

### 2. Set Environment Variables

Edit `.env` with your API keys:

```bash
# Required: at least one LLM provider
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...

# Optional: vector store configuration
VECTOR_STORE_TYPE=chroma     # chroma | faiss | pinecone
CHROMA_PERSIST_DIR=./chromadb

# Optional: database and caching
DATABASE_URL=postgresql://user:pass@localhost:5432/ragdb
REDIS_URL=redis://localhost:6379
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using Make:

```bash
make install
```

### 5. Run the Server

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Or using Make:

```bash
make run
```

### 6. Verify

```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"Adaptive RAG Pipeline"}
```

### 7. Run Tests

```bash
pytest tests/ -v --cov=backend
```

Or using Make:

```bash
make test
```

### 8. Lint

```bash
ruff check .
ruff format --check .
```

Or using Make:

```bash
make lint
```

---

## Docker Compose Deployment

### Architecture

```
                          +-----------------+
                          |    Frontend     |
                          |  (React on  :3000) |
                          +-------+---------+
                                  |
                          REACT_APP_API_URL
                                  |
                                  v
+-----------------+       +-----------------+       +-----------------+
|    Backend      |       |   PostgreSQL    |       |     Redis       |
|  (FastAPI       |------>|  (port 5432)    |       |  (port 6379)    |
|   on :8000)     |       +-----------------+       +-----------------+
+--------+--------+
         |
         v
  ./chromadb (volume)
```

### docker-compose.yml

```yaml
version: "3.9"

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - postgres
      - redis
    volumes:
      - ./chromadb:/app/chromadb
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: ragdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Deployment Steps

```bash
# Build and start all services
docker-compose up --build

# Or using Make
make docker-up

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Stop and remove volumes (destroys database data)
docker-compose down -v
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_NAME` | No | `Adaptive RAG Pipeline` | Application name (shown in health check and OpenAPI docs) |
| `DEBUG` | No | `true` | Enable debug mode |
| `LOG_LEVEL` | No | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `OPENAI_API_KEY` | Yes* | — | OpenAI API key (required if using OpenAILLM) |
| `OPENAI_MODEL` | No | `gpt-4` | OpenAI model name |
| `ANTHROPIC_API_KEY` | Yes* | — | Anthropic API key (required if using ClaudeLLM) |
| `ANTHROPIC_MODEL` | No | `claude-3-opus-20240229` | Anthropic model name |
| `GROQ_API_KEY` | Yes* | — | Groq API key (required if using GroqLLM) |
| `GROQ_MODEL` | No | `mixtral-8x7b-32768` | Groq model name |
| `EMBEDDING_PROVIDER` | No | `openai` | Embedding provider |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` | Embedding model name |
| `VECTOR_STORE_TYPE` | No | `chroma` | Vector store backend: `chroma`, `faiss`, `pinecone` |
| `CHROMA_PERSIST_DIR` | No | `./chromadb` | ChromaDB persistence directory |
| `PINECONE_API_KEY` | Yes* | — | Pinecone API key (required if using PineconeStore) |
| `PINECONE_ENVIRONMENT` | Yes* | — | Pinecone environment |
| `PINECONE_INDEX` | Yes* | — | Pinecone index name |
| `SEARCH_PROVIDER` | No | `duckduckgo` | Web search provider |
| `GOOGLE_API_KEY` | Yes* | — | Google Custom Search API key |
| `GOOGLE_CSE_ID` | Yes* | — | Google Custom Search Engine ID |
| `DATABASE_URL` | No | — | PostgreSQL connection string (e.g., `postgresql://user:pass@localhost:5432/ragdb`) |
| `REDIS_URL` | No | — | Redis connection string (e.g., `redis://localhost:6379`) |

\* Required only if the corresponding provider is used. At least one LLM API key must be configured.

---

## Production Considerations

### CORS

In production, restrict CORS origins to your frontend domain:

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Replace with actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Secrets Management

Do NOT commit `.env` files with real secrets to version control. Use:

- **Docker secrets** (`docker secret create`)
- **Cloud secret stores** (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
- **CI/CD secrets** (GitHub Actions secrets, GitLab CI variables)

### Volumes

Persistent data volumes in production:

| Path | Service | Purpose |
|------|---------|---------|
| `./chromadb` | Backend | ChromaDB vector index persistence |
| `postgres_data` | PostgreSQL | Database files |
| *(none)* | Redis | Can be recreated from persistence config |

### Health Checks

Add health check configurations to docker-compose:

```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### Resource Limits

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: "2"
        memory: "4G"
      reservations:
        cpus: "1"
        memory: "2G"
```

### Reverse Proxy (Nginx)

For production, front with Nginx for SSL termination, rate limiting, and load balancing:

```nginx
server {
    listen 443 ssl;
    server_name api.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/api.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.your-domain.com/privkey.pem;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/v1/query {
        limit_req zone=querylimiter burst=20 nodelay;
        proxy_pass http://backend:8000;
    }
}
```

### Logging

In production, configure structured logging for log aggregation:

```python
# backend/utils/logger.py
import json
import logging


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_entry)
```

---

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run lint
        run: |
          pip install ruff
          ruff check .
      - name: Run tests
        run: |
          pip install pytest pytest-asyncio pytest-cov
          pytest tests/ -v --cov=backend
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

  build-and-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t adaptive-rag-pipeline .
      - name: Push to registry
        run: |
          docker tag adaptive-rag-pipeline ${{ secrets.REGISTRY_URL }}/adaptive-rag-pipeline:latest
          docker push ${{ secrets.REGISTRY_URL }}/adaptive-rag-pipeline:latest
      - name: Deploy
        run: |
          # Deploy to your target environment
          # e.g., SSH into server, pull image, restart containers
          echo "Deploying..."
```

### Pipeline Stages

1. **Lint**: `ruff check .` — code quality and style checks
2. **Test**: `pytest tests/ -v --cov=backend` — unit and integration tests with coverage
3. **Build**: `docker build -t adaptive-rag-pipeline .` — container image build
4. **Push**: Push image to container registry (Docker Hub, ECR, ACR, GCR)
5. **Deploy**: Deploy to target environment (Kubernetes, Docker Compose, cloud VM)

---

## Quick Reference

```bash
# Development
cp .env.example .env          # Configure environment
python -m venv venv            # Create virtual environment
source venv/bin/activate       # Activate it
pip install -r requirements.txt # Install dependencies
uvicorn backend.main:app --reload  # Start server

# Testing
pytest tests/ -v               # Run all tests
pytest tests/unit/ -v          # Run unit tests only
pytest tests/integration/ -v   # Run integration tests only

# Docker
docker-compose up --build      # Start all services
docker-compose down            # Stop all services
docker-compose logs -f backend # Follow backend logs

# Maintenance
make clean                     # Clean cache files
ruff check .                   # Lint
ruff format .                  # Format code
```
