from __future__ import annotations

import asyncio

import pytest

from app.models.chat import AIResponse, ChatMessage, KnowledgeChunk
from app.services.ai_service import AIServiceError
from app.services.azure_ai_service import AzureAIService


class StubAzureClient:
    """Mock httpx.AsyncClient for testing Azure Responses API endpoint."""

    def __init__(self, *, output_text: str = "Pret response"):
        self.output_text = output_text
        self.calls: list[dict[str, object]] = []

    async def post(self, url: str, **kwargs: object) -> object:
        """Mock POST request to /responses endpoint."""
        self.calls.append(kwargs)
        # Azure Responses API returns {"output": [{"content": [{"text": "..."}]}]}
        response_data = {
            "output": [
                {
                    "content": [
                        {
                            "text": self.output_text,
                        }
                    ]
                }
            ]
        }
        return StubResponse(response_data)


class StubResponse:
    """Mock httpx response object."""

    def __init__(self, data: dict) -> None:
        self.data = data
        self.status_code = 200
        self.text = ""

    def raise_for_status(self) -> None:
        """No-op for stub."""
        pass

    def json(self) -> dict:
        """Return mock response data."""
        return self.data


def test_azure_ai_service_successful_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "pret-assistant-poc")

    service = AzureAIService(client=StubAzureClient(output_text="Operational help here."))
    result = asyncio.run(
        service.generate_response(
            [ChatMessage(role="user", content="The coffee machine is broken")],
            [],
        )
    )

    assert isinstance(result, AIResponse)
    assert result.message == "Operational help here."


def test_azure_ai_service_includes_system_instructions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "pret-assistant-poc")

    client = StubAzureClient(output_text="Need more detail.")
    service = AzureAIService(client=client)
    asyncio.run(
        service.generate_response(
            [ChatMessage(role="user", content="The coffee machine is broken")],
            [],
        )
    )

    payload = client.calls[0]
    json_data = payload["json"]
    messages = json_data["input"]
    assert messages[0]["type"] == "message"
    assert messages[0]["role"] == "system"
    assert "Pret Employee Assistant" in messages[0]["content"]
    assert messages[1]["type"] == "message"
    assert messages[1]["content"] == "The coffee machine is broken"


def test_azure_ai_service_forwards_conversation_context(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "pret-assistant-poc")

    client = StubAzureClient(output_text="Okay.")
    service = AzureAIService(client=client)
    knowledge: list[KnowledgeChunk] = [KnowledgeChunk(content="coffee machine troubleshooting", source="manual")]

    asyncio.run(
        service.generate_response(
            [
                ChatMessage(role="user", content="The coffee machine is broken"),
                ChatMessage(role="assistant", content="I can help."),
            ],
            knowledge,
        )
    )

    payload = client.calls[0]
    json_data = payload["json"]
    assert json_data["model"] == "pret-assistant-poc"
    assert json_data["input"][-1]["type"] == "message"
    assert json_data["input"][-1]["content"] == "I can help."


def test_azure_ai_service_handles_provider_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "pret-assistant-poc")

    class FailingClient:
        async def post(self, url: str, **kwargs: object) -> object:
            raise RuntimeError("upstream failure")

    service = AzureAIService(client=FailingClient())

    with pytest.raises(AIServiceError, match="AI provider request failed"):
        asyncio.run(
            service.generate_response([ChatMessage(role="user", content="The machine is broken")], [])
        )
