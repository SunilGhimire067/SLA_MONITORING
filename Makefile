.PHONY: help up down build dev logs migrate seed shell-backend shell-frontend test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ──── Docker Commands ────

up: ## Start all services (production)
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Build all containers
	docker compose build

dev: ## Start in development mode (with hot reload)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-down: ## Stop development services
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

logs: ## View logs for all services
	docker compose logs -f

logs-backend: ## View backend logs
	docker compose logs -f backend

logs-celery: ## View celery worker logs
	docker compose logs -f celery-worker

# ──── Database Commands ────

migrate: ## Run database migrations
	docker compose exec backend alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="add users table")
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed database with demo data
	docker compose exec backend python -m app.scripts.seed_data

# ──── Shell Access ────

shell-backend: ## Open shell in backend container
	docker compose exec backend bash

shell-db: ## Open MySQL shell
	docker compose exec mysql mysql -u itsm_user -p itsm_db

shell-redis: ## Open Redis CLI
	docker compose exec redis redis-cli

# ──── Testing ────

test: ## Run backend tests
	docker compose exec backend pytest tests/ -v

test-cov: ## Run tests with coverage
	docker compose exec backend pytest tests/ -v --cov=app --cov-report=html

# ──── Maintenance ────

clean: ## Remove all containers, volumes, and images
	docker compose down -v --rmi all --remove-orphans

restart: ## Restart all services
	docker compose restart

status: ## Show service status
	docker compose ps
