.PHONY: help dev-backend dev-frontend dev test lint migrate seed docker-up docker-down docker-logs clean

PYTHON      := backend/venv/bin/python
PIP         := backend/venv/bin/pip
PYTEST      := backend/venv/bin/python -m pytest
ALEMBIC     := backend/venv/bin/alembic

help:
	@echo "Universal AI File Converter — developer commands"
	@echo ""
	@echo "  make setup          Install all backend + frontend dependencies"
	@echo "  make dev            Start both backend and frontend in dev mode"
	@echo "  make dev-backend    Run FastAPI with --reload on :8000"
	@echo "  make dev-frontend   Run Vite dev server on :5173"
	@echo "  make test           Run the full pytest suite"
	@echo "  make migrate        Apply Alembic migrations"
	@echo "  make migrate-new    Generate a new migration (MSG=... make migrate-new)"
	@echo "  make lint           Run ruff linter on backend source"
	@echo "  make docker-up      Start all services via Docker Compose"
	@echo "  make docker-down    Stop all services"
	@echo "  make docker-logs    Follow all service logs"
	@echo "  make clean          Remove __pycache__, .pyc, dev.db, node_modules"

# ─── Setup ─────────────────────────────────────────────────────────────────
setup: setup-backend setup-frontend

setup-backend:
	cd backend && python3 -m venv venv && $(PIP) install --upgrade pip -q
	$(PIP) install -r backend/requirements.txt

setup-frontend:
	cd frontend && npm install

# ─── Dev servers ───────────────────────────────────────────────────────────
dev:
	@echo "Starting backend (port 8000) and frontend (port 5173) in parallel..."
	@make -j 2 dev-backend dev-frontend

dev-backend:
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# ─── Tests ─────────────────────────────────────────────────────────────────
test:
	cd backend && $(PYTEST) tests/ -v

# ─── Migrations ────────────────────────────────────────────────────────────
migrate:
	cd backend && $(ALEMBIC) upgrade head

migrate-new:
	cd backend && $(ALEMBIC) revision --autogenerate -m "$(MSG)"

# ─── Lint ──────────────────────────────────────────────────────────────────
lint:
	cd backend && $(PYTHON) -m ruff check app/ tests/ --fix

# ─── Docker ────────────────────────────────────────────────────────────────
docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f --tail=100

# ─── Cleanup ───────────────────────────────────────────────────────────────
clean:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find backend -name "*.pyc" -delete 2>/dev/null; true
	rm -f backend/dev.db
	rm -rf backend/storage_data
	rm -rf frontend/node_modules
	rm -rf frontend/dist
