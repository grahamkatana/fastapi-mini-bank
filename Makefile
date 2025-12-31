.PHONY: help install run celery test pytest docker-up docker-down clean lint security format

help:
	@echo "FastAPI Project - Available Commands (using uv)"
	@echo "================================================"
	@echo "make install      - Install dependencies with uv"
	@echo "make sync         - Sync dependencies (faster)"
	@echo "make run          - Run FastAPI server"
	@echo "make celery       - Run Celery worker"
	@echo "make test         - Run manual test script"
	@echo "make pytest       - Run pytest tests"
	@echo "make coverage     - Run tests with coverage report"
	@echo "make format       - Format code with ruff"
	@echo "make lint         - Run code linting"
	@echo "make security     - Run security scans"
	@echo "make ci           - Run all CI checks"
	@echo "make docker-up    - Start all services with Docker"
	@echo "make docker-down  - Stop all Docker services"
	@echo "make clean        - Clean up cache files"

install:
	uv pip install -e ".[dev]"

sync:
	uv pip sync

run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

celery:
	uv run celery -A app.tasks.celery_app worker --loglevel=info

celery-beat:
	uv run celery -A app.tasks.celery_app beat --loglevel=info

test:
	uv run python test_api.py

pytest:
	uv run pytest tests/ -v

coverage:
	uv run pytest --cov=app --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	@echo "Running ruff linting..."
	uv run ruff check app tests
	@echo "Running type checking..."
	uv run mypy app --ignore-missing-imports

security:
	@echo "Running Bandit security scan..."
	uv pip install bandit
	uv run bandit -r app -f json -o bandit-report.json || true
	@echo "Checking for known vulnerabilities..."
	uv pip install safety
	uv run safety check || true

ci: format lint pytest security
	@echo "All CI checks completed!"

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

dev:
	@echo "Starting development environment..."
	@make docker-up
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services ready!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
