# DevOps Monitoring Dashboard

A real-time system monitoring dashboard built entirely in Python. It features a FastAPI backend that exposes system metrics (CPU, memory, disk) via REST and WebSocket endpoints, and a Streamlit frontend that displays live KPIs and charts.

## Architecture

```
┌─────────────────────────────────┐
│       Docker Compose            │
│                                 │
│  ┌───────────────────────────┐  │
│  │  api (FastAPI — :8000)    │  │
│  │  ├── GET  /health         │  │
│  │  ├── GET  /metrics        │  │
│  │  ├── WS   /ws/metrics     │  │
│  │  ├── POST /servers        │  │
│  │  ├── GET  /servers        │  │
│  │  ├── DELETE /servers/{id} │  │
│  │  └── POST /servers/{id}/  │  │
│  │         check             │  │
│  └───────────────────────────┘  │
│              ▲                  │
│              │ http://api:8000  │
│              ▼                  │
│  ┌───────────────────────────┐  │
│  │  dashboard (Streamlit     │  │
│  │            — :8501)       │  │
│  │  ├── Metrics tab (KPIs   │  │
│  │  │   + live chart)        │  │
│  │  └── Servers tab (table   │  │
│  │      + registration form) │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

## Tech Stack

| Layer          | Technology                     |
|----------------|--------------------------------|
| Language       | Python 3.11                    |
| API Framework  | FastAPI + Uvicorn (ASGI)       |
| Frontend       | Streamlit                      |
| HTTP Client    | httpx                          |
| System Metrics | psutil                         |
| Auth           | API Key (`X-API-Key` header)   |
| Containers     | Docker, Docker Compose         |
| Tests          | pytest, FastAPI TestClient      |
| CI             | GitHub Actions                 |

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Make

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd Python-Project-Rendu

# 2. Create your .env file
cp .env.example .env
# Edit .env and set your API_KEY value

# 3. Start the full stack
make up

# 4. Open in your browser
#    API docs:   http://localhost:8000/docs
#    Dashboard:  http://localhost:8501
```

## Makefile Commands

| Command                | Description                                        |
|------------------------|----------------------------------------------------|
| `make up`              | Build and start all services in detached mode       |
| `make down`            | Stop and remove all services and volumes            |
| `make logs`            | Follow container logs                               |
| `make test`            | Run unit tests with coverage (>= 75% required)      |
| `make lint`            | Run flake8 linter                                   |
| `make dev`             | Show instructions for local development             |
| `make dev-api`         | Start the API locally with hot-reload               |
| `make dev-dashboard`   | Start the Streamlit dashboard locally               |
| `make integration-test`| Start Docker stack and run integration tests        |

## Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1 — start the API
make dev-api

# Terminal 2 — start the dashboard
make dev-dashboard
```

## Running Tests

```bash
# Unit and route tests (no Docker required)
make test

# Lint check
make lint

# Integration tests (requires Docker)
make integration-test
```

## Environment Variables

| Variable       | Description                                | Default               |
|----------------|--------------------------------------------|-----------------------|
| `API_KEY`      | API key for protected endpoints            | *(required)*          |
| `API_BASE_URL` | URL the dashboard uses to reach the API    | `http://api:8000`     |

## API Endpoints

| Method   | Endpoint              | Auth     | Description                        |
|----------|-----------------------|----------|------------------------------------|
| `GET`    | `/health`             | No       | Liveness probe                     |
| `GET`    | `/metrics`            | No       | CPU, memory, disk usage            |
| `WS`     | `/ws/metrics`         | No       | Live metrics stream (1 frame/sec)  |
| `POST`   | `/servers`            | API Key  | Register a server to monitor       |
| `GET`    | `/servers`            | No       | List all servers and their status  |
| `DELETE` | `/servers/{id}`       | API Key  | Remove a server                    |
| `POST`   | `/servers/{id}/check` | No       | Trigger a manual health check      |

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push and PR to `main`:

```
lint ─┐
test ─┤── integration-test ── build (main only)
```

| Job                | Description                                     |
|--------------------|-------------------------------------------------|
| `lint`             | flake8 code quality check                       |
| `test`             | Unit + route tests with coverage >= 75%         |
| `integration-test` | Starts Docker Compose and runs end-to-end tests |
| `build`            | Builds API and Dashboard Docker images          |

## Project Structure

```
├── api/                          # FastAPI backend
│   ├── __init__.py
│   ├── main.py                   # App, lifespan, routes, WebSocket
│   ├── models.py                 # Server dataclass + Pydantic schemas
│   ├── auth.py                   # API key dependency
│   ├── metrics.py                # System metrics via psutil
│   ├── poller.py                 # Async polling loop
│   └── Dockerfile                # Multi-stage build
│
├── dashboard/                    # Streamlit frontend
│   ├── app.py
│   └── Dockerfile
│
├── tests/
│   ├── conftest.py               # Test configuration
│   ├── test_metrics.py           # Unit tests for metrics module
│   ├── test_routes.py            # API route tests (TestClient)
│   └── test_integration.py       # Docker integration tests
│
├── .github/workflows/
│   └── ci-cd.yml                 # Lint → Test → Build
│
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── Makefile
├── requirements.txt
├── setup.cfg
└── README.md
```
