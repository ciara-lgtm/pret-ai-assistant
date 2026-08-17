from __future__ import annotations

from typing import Protocol

from app.models.chat import AIResponse, ChatMessage, KnowledgeChunk


class AIService(Protocol):
    """Provider-independent interface for generating AI responses."""

    async def generate_response(
        self,
        conversation: list[ChatMessage],
        knowledge_context: list[KnowledgeChunk],
    ) -> AIResponse:
        """Generate a response from prior conversation and relevant knowledge."""
        ...
