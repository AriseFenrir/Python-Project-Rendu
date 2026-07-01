.PHONY: up down logs test lint dev dev-api dev-dashboard integration-test

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f

test:
	pytest tests/ -v --cov=api --cov-fail-under=75 --ignore=tests/test_integration.py

lint:
	flake8 api/ dashboard/ tests/

dev:
	@echo "Start the API and dashboard in separate terminals:"
	@echo "  Terminal 1: make dev-api"
	@echo "  Terminal 2: make dev-dashboard"

dev-api:
	uvicorn api.main:app --reload --port 8000

dev-dashboard:
	API_BASE_URL=http://localhost:8000 streamlit run dashboard/app.py --server.port 8501

integration-test:
	docker compose up --build -d
	@echo "Waiting for services to be healthy..."
	@sleep 15
	RUN_INTEGRATION_TESTS=1 pytest tests/test_integration.py -v; \
	status=$$?; \
	docker compose down -v; \
	exit $$status
