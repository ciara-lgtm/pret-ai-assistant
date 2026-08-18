from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIServiceError
from app.services.azure_ai_service import azure_ai_service
from app.services.chat_service import ChatService
from app.services.fake_ai_service import fake_ai_service
from app.services.local_knowledge_retriever import local_knowledge_retriever

router = APIRouter(prefix="/api/v1", tags=["chat"])


def get_chat_service() -> ChatService:
    """Provide the configured AI-backed ChatService for the route layer."""
    use_fake_ai = os.getenv("USE_FAKE_AI", "true").lower() not in {"0", "false", "no"}
    if use_fake_ai:
        return ChatService(fake_ai_service(), retriever=local_knowledge_retriever())

    return ChatService(azure_ai_service(), retriever=local_knowledge_retriever())


@router.post("/chat", response_model=ChatResponse)
async def create_chat_completion(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Accept a user chat request and return an assistant response."""
    try:
        return await chat_service.process_message(request)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail="AI service unavailable.") from exc
