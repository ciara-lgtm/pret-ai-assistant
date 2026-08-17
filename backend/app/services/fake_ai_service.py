from __future__ import annotations

from app.models.chat import AIResponse, ChatMessage, KnowledgeChunk
from app.services.ai_service import AIService


class FakeAIService:
    """Development-only placeholder implementation used until a real AI provider is added."""

    async def generate_response(
        self,
        conversation: list[ChatMessage],
        knowledge_context: list[KnowledgeChunk],
    ) -> AIResponse:
        """Return a placeholder AI reply based on the latest user message only."""
        latest_message = conversation[-1].content if conversation else "No message received."
        knowledge_note = (
            f" Relevant context available: {len(knowledge_context)} knowledge item(s)."
            if knowledge_context
            else ""
        )
        return AIResponse(message=f"Thanks for the update: {latest_message}.{knowledge_note}")


def fake_ai_service() -> AIService:
    """Factory for the development placeholder AI service."""
    return FakeAIService()
