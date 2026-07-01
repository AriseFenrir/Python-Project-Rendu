import os

import pytest
from fastapi.testclient import TestClient

from api.main import app, servers

API_KEY = os.environ.get("API_KEY", "test-key")


@pytest.fixture(autouse=True)
def clear_servers():
    servers.clear()
    yield
    servers.clear()


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "cpu_percent" in data
    assert "memory_percent" in data
    assert "disk_percent" in data


def test_create_server_without_api_key():
    response = client.post(
        "/servers",
        json={"name": "test", "host": "localhost", "port": 8080},
    )
    assert response.status_code == 403


def test_create_server_with_invalid_api_key():
    response = client.post(
        "/servers",
        json={"name": "test", "host": "localhost", "port": 8080},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 403


def test_create_server_with_api_key():
    response = client.post(
        "/servers",
        json={"name": "test", "host": "localhost", "port": 8080},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test"
    assert data["host"] == "localhost"
    assert data["port"] == 8080
    assert data["status"] == "UNKNOWN"
    assert "id" in data


def test_list_servers_empty():
    response = client.get("/servers")
    assert response.status_code == 200
    assert response.json() == []


def test_list_servers_with_data():
    client.post(
        "/servers",
        json={"name": "srv1", "host": "localhost", "port": 8080},
        headers={"X-API-Key": API_KEY},
    )
    client.post(
        "/servers",
        json={"name": "srv2", "host": "localhost", "port": 9090},
        headers={"X-API-Key": API_KEY},
    )
    response = client.get("/servers")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_server():
    response = client.post(
        "/servers",
        json={"name": "test", "host": "localhost", "port": 8080},
        headers={"X-API-Key": API_KEY},
    )
    server_id = response.json()["id"]

    response = client.delete(
        f"/servers/{server_id}",
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 204

    response = client.get("/servers")
    assert len(response.json()) == 0


def test_delete_server_not_found():
    response = client.delete(
        "/servers/nonexistent",
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 404


def test_delete_server_without_api_key():
    response = client.post(
        "/servers",
        json={"name": "test", "host": "localhost", "port": 8080},
        headers={"X-API-Key": API_KEY},
    )
    server_id = response.json()["id"]

    response = client.delete(f"/servers/{server_id}")
    assert response.status_code == 403


def test_check_server():
    response = client.post(
        "/servers",
        json={"name": "test", "host": "localhost", "port": 8080},
        headers={"X-API-Key": API_KEY},
    )
    server_id = response.json()["id"]

    response = client.post(f"/servers/{server_id}/check")
    assert response.status_code == 200
    assert response.json()["status"] in ["UP", "DOWN", "DEGRADED"]


def test_check_server_not_found():
    response = client.post("/servers/nonexistent/check")
    assert response.status_code == 404


def test_create_server_invalid_port_too_high():
    response = client.post(
        "/servers",
        json={"name": "test", "host": "localhost", "port": 99999},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 422


def test_create_server_invalid_port_zero():
    response = client.post(
        "/servers",
        json={"name": "test", "host": "localhost", "port": 0},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 422


def test_websocket_metrics():
    with client.websocket_connect("/ws/metrics") as ws:
        data = ws.receive_json()
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "disk_percent" in data


def test_websocket_metrics_values_valid():
    with client.websocket_connect("/ws/metrics") as ws:
        data = ws.receive_json()
        assert 0 <= data["cpu_percent"] <= 100
        assert 0 <= data["memory_percent"] <= 100
        assert 0 <= data["disk_percent"] <= 100
