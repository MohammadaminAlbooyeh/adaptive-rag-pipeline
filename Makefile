.PHONY: install run test lint clean docker-up docker-build

install:
	pip install -r requirements.txt

run:
	uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest tests/ -v --cov=backend

lint:
	ruff check .
	ruff format --check .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf chromadb/

docker-build:
	docker-compose build

docker-up:
	docker-compose up
