from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_exposes_typed_configuration():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["provider"] == "mock"


def test_openapi_registers_chat_routes():
    schema = client.get("/openapi.json").json()

    assert "/api/chat" in schema["paths"]
    assert "/api/chat/confirm" in schema["paths"]
    assert "/health" in schema["paths"]
