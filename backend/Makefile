.PHONY: up down dev build shell logs test format lint migrate auto-migrate help db-up

# Default command
help:
	@echo "Available commands:"
	@echo "  make up          - Start all services (Docker)"
	@echo "  make down        - Stop all services"
	@echo "  make dev         - Run FastAPI locally with Uvicorn (live reload)"
	@echo "  make build       - Rebuild Docker images"
	@echo "  make shell       - Open a shell inside the backend container"
	@echo "  make logs        - Tail logs for all services"
	@echo "  make test        - Run tests locally"
	@echo "  make format      - Run Ruff format and isort"
	@echo "  make lint        - Run Ruff and MyPy"
	@echo "  make migrate     - Run database migrations"
	@echo "  make auto-migrate- Generate a new migration automatically"
	@echo "  make db-up       - Start just the database and Redis"

# Docker commands
up:
	docker-compose -f ../docker-compose.yml up -d

down:
	docker-compose -f ../docker-compose.yml down

build:
	docker-compose -f ../docker-compose.yml build

shell:
	docker-compose -f ../docker-compose.yml exec api /bin/bash

logs:
	docker-compose -f ../docker-compose.yml logs -f

db-up:
	docker-compose -f ../docker-compose.yml up -d postgres redis

# Local development commands
dev: db-up
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

format:
	ruff check --select I --fix .
	ruff format .

lint:
	ruff check .
	mypy app

# Database migration commands
migrate:
	alembic upgrade head

auto-migrate:
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"
