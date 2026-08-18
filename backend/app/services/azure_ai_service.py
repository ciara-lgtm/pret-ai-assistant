from __future__ import annotations

import logging
import os

import httpx

from app.models.chat import AIResponse, ChatMessage, KnowledgeChunk
from app.services.ai_service import AIService, AIServiceError
from app.services.system_instructions import SYSTEM_INSTRUCTIONS

logger = logging.getLogger(__name__)


class AzureAIService:
    """Concrete Azure Foundry implementation using /v1/responses endpoint."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.client = client
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    def _build_messages(self, conversation: list[ChatMessage]) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [
            {"type": "message", "role": "system", "content": SYSTEM_INSTRUCTIONS}
        ]
        for message in conversation:
            messages.append({
                "type": "message",
                "role": message.role,
                "content": message.content
            })
        return messages

    async def generate_response(
        self,
        conversation: list[ChatMessage],
        knowledge_context: list[KnowledgeChunk],
    ) -> AIResponse:
        """Generate a response using the configured Azure Foundry /responses endpoint."""
        if not self.api_key or not self.endpoint:
            raise AIServiceError("Azure OpenAI configuration is missing.")

        try:
            payload = {
                "input": self._build_messages(conversation),
                "model": self.deployment,
                "temperature": 0.2,
            }
            
            if self.client:
                response = await self.client.post(
                    self.endpoint,
                    headers={"api-key": self.api_key},
                    json=payload,
                    timeout=30.0,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.endpoint,
                        headers={"api-key": self.api_key},
                        json=payload,
                        timeout=30.0,
                    )
            
            if response.status_code != 200:
                error_detail = response.text if response.text else "No error detail"
                logger.error("Azure returned %d: %s", response.status_code, error_detail)
            
            response.raise_for_status()
            data = response.json()
            content = self._extract_response_content(data)
            return AIResponse(message=content.strip() or "I could not generate a response.")
        except Exception as exc:  # pragma: no cover - defensive boundary
            logger.exception(
                "Azure OpenAI request failed with %s: %s",
                type(exc).__name__,
                str(exc),
            )
            raise AIServiceError("AI provider request failed.") from exc

    def _extract_response_content(self, data: dict) -> str:
        """Extract text content from Azure Responses API response format.
        
        Expected format: {"output": [{"content": [{"text": "..."}]}]}
        """
        output = data.get("output", [])
        if output and isinstance(output, list) and len(output) > 0:
            first_output = output[0]
            if isinstance(first_output, dict):
                content_list = first_output.get("content", [])
                if content_list and isinstance(content_list, list) and len(content_list) > 0:
                    return content_list[0].get("text", "")
        return ""




def azure_ai_service() -> AIService:
    """Factory for the Azure-backed AI service."""
    return AzureAIService()
