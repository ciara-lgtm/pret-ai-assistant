from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(..., description="The role of the message author.")
    content: str = Field(..., min_length=1, description="The message content.")


class KnowledgeChunk(BaseModel):
    content: str = Field(..., description="Retrieved knowledge snippet relevant to the user request.")
    source: str | None = Field(default=None, description="Optional source label for the knowledge chunk.")


class AIResponse(BaseModel):
    message: str = Field(..., min_length=1, description="Generated response text from the AI layer.")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user message to process.")
    conversation_id: str | None = Field(default=None, description="Optional existing conversation identifier.")


class ChatResponse(BaseModel):
    message: str = Field(..., min_length=1, description="The generated assistant reply.")
    conversation_id: str = Field(..., description="The conversation identifier used for this interaction.")
    status: str = Field(default="success", description="Current state of the chat response.")
