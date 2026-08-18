from __future__ import annotations

from typing import Protocol

from app.models.chat import AIResponse, ChatMessage, KnowledgeChunk


class AIServiceError(RuntimeError):
    """Raised when the configured AI provider is unavailable or returns an error."""


class AIService(Protocol):
    """Provider-independent interface for generating AI responses."""

    async def generate_response(
        self,
        conversation: list[ChatMessage],
        knowledge_context: list[KnowledgeChunk],
    ) -> AIResponse:
        """Generate a response from prior conversation and relevant knowledge."""
        ...
