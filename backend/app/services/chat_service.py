from __future__ import annotations

import uuid

from app.models.chat import AIResponse, ChatMessage, ChatRequest, ChatResponse, KnowledgeChunk
from app.services.ai_service import AIService


class ChatService:
    """Orchestrates chat requests and delegates AI generation to a provider-specific service."""

    def __init__(self, ai_service: AIService) -> None:
        self.ai_service = ai_service

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a user message and return a typed assistant reply."""
        conversation_id = request.conversation_id or f"conversation-{uuid.uuid4()}"

        messages = [
            ChatMessage(role="user", content=request.message),
        ]
        knowledge_context: list[KnowledgeChunk] = []

        response: AIResponse = await self.ai_service.generate_response(messages, knowledge_context)

        return ChatResponse(
            message=response.message,
            conversation_id=conversation_id,
            status="success",
        )
