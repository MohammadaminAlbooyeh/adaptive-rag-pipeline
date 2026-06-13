# Deployment

## Docker

```bash
docker-compose up --build
```

## Manual

```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
