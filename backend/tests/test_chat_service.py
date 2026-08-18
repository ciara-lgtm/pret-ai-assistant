from __future__ import annotations

import asyncio

from app.models.chat import AIResponse, ChatMessage, ChatRequest, KnowledgeChunk
from app.services.chat_service import ChatService


class StubAIService:
    async def generate_response(
        self,
        conversation: list[ChatMessage],
        knowledge_context: list[KnowledgeChunk],
    ) -> AIResponse:
        assert conversation[0].content == "The coffee machine is broken"
        assert knowledge_context
        assert any("coffee_machine_broken.md" in chunk.source for chunk in knowledge_context)
        return AIResponse(message="I can help with that.")


def test_chat_service_uses_ai_service() -> None:
    service = ChatService(StubAIService())

    response = asyncio.run(
        service.process_message(
            ChatRequest(message="The coffee machine is broken", conversation_id="conv-42")
        )
    )

    assert response.conversation_id == "conv-42"
    assert response.message == "I can help with that."
    assert response.status == "success"


def test_chat_service_generates_default_conversation_id() -> None:
    service = ChatService(StubAIService())

    response = asyncio.run(service.process_message(ChatRequest(message="The coffee machine is broken")))

    assert response.conversation_id.startswith("conversation-")
    assert response.status == "success"
