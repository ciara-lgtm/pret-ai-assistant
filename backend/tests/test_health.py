from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "pret-ai-assistant"


def test_chat_endpoint_success() -> None:
    response = client.post(
        "/api/v1/chat",
        json={"message": "The coffee machine is broken", "conversation_id": "conv-123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["conversation_id"] == "conv-123"
    assert payload["status"] == "success"
    assert payload["message"]


def test_chat_endpoint_requires_message() -> None:
    response = client.post("/api/v1/chat", json={"conversation_id": "conv-123"})

    assert response.status_code == 422


def test_chat_endpoint_handles_missing_conversation_id() -> None:
    response = client.post("/api/v1/chat", json={"message": "The coffee machine is broken"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["conversation_id"].startswith("conversation-")
    assert len(payload["conversation_id"]) > len("conversation-")
    assert payload["status"] == "success"
