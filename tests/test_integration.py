import os

import httpx
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="Set RUN_INTEGRATION_TESTS=1 to run integration tests",
)

API_URL = os.getenv("API_URL", "http://localhost:8000")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:8501")
API_KEY = os.getenv("API_KEY", "changeme")


class TestAPIHealth:
    def test_health_endpoint(self):
        response = httpx.get(f"{API_URL}/health", timeout=10)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_metrics_endpoint(self):
        response = httpx.get(f"{API_URL}/metrics", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "disk_percent" in data

    def test_docs_endpoint(self):
        response = httpx.get(f"{API_URL}/docs", timeout=10)
        assert response.status_code == 200


class TestAPIServerCRUD:
    def test_full_server_lifecycle(self):
        # Create
        response = httpx.post(
            f"{API_URL}/servers",
            json={"name": "integration-test", "host": "api", "port": 8000},
            headers={"X-API-Key": API_KEY},
            timeout=10,
        )
        assert response.status_code == 201
        server_id = response.json()["id"]
        assert response.json()["name"] == "integration-test"

        # List
        response = httpx.get(f"{API_URL}/servers", timeout=10)
        assert response.status_code == 200
        ids = [s["id"] for s in response.json()]
        assert server_id in ids

        # Check
        response = httpx.post(
            f"{API_URL}/servers/{server_id}/check", timeout=10
        )
        assert response.status_code == 200
        assert response.json()["status"] in ["UP", "DOWN", "DEGRADED"]

        # Delete
        response = httpx.delete(
            f"{API_URL}/servers/{server_id}",
            headers={"X-API-Key": API_KEY},
            timeout=10,
        )
        assert response.status_code == 204

        # Verify deleted
        response = httpx.get(f"{API_URL}/servers", timeout=10)
        ids = [s["id"] for s in response.json()]
        assert server_id not in ids

    def test_auth_required(self):
        response = httpx.post(
            f"{API_URL}/servers",
            json={"name": "test", "host": "localhost", "port": 80},
            timeout=10,
        )
        assert response.status_code == 403

    def test_invalid_port_rejected(self):
        response = httpx.post(
            f"{API_URL}/servers",
            json={"name": "test", "host": "localhost", "port": 99999},
            headers={"X-API-Key": API_KEY},
            timeout=10,
        )
        assert response.status_code == 422


class TestDashboard:
    def test_dashboard_accessible(self):
        response = httpx.get(DASHBOARD_URL, timeout=10)
        assert response.status_code == 200

    def test_dashboard_returns_html(self):
        response = httpx.get(DASHBOARD_URL, timeout=10)
        assert "text/html" in response.headers.get("content-type", "")


class TestInterServiceCommunication:
    def test_server_pointing_to_api_gets_checked(self):
        # Register the API itself as a monitored server
        response = httpx.post(
            f"{API_URL}/servers",
            json={"name": "self-api", "host": "api", "port": 8000},
            headers={"X-API-Key": API_KEY},
            timeout=10,
        )
        assert response.status_code == 201
        server_id = response.json()["id"]

        # Trigger a health check — the API should reach itself via Docker networking
        response = httpx.post(
            f"{API_URL}/servers/{server_id}/check", timeout=10
        )
        assert response.status_code == 200
        assert response.json()["status"] == "UP"

        # Cleanup
        httpx.delete(
            f"{API_URL}/servers/{server_id}",
            headers={"X-API-Key": API_KEY},
            timeout=10,
        )
