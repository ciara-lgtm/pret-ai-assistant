from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.fake_ai_service import fake_ai_service

router = APIRouter(prefix="/api/v1", tags=["chat"])


def get_chat_service() -> ChatService:
    """Provide a ChatService instance for the route layer."""
    return ChatService(fake_ai_service())


@router.post("/chat", response_model=ChatResponse)
async def create_chat_completion(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Accept a user chat request and return an assistant response."""
    return await chat_service.process_message(request)
