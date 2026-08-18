from __future__ import annotations

import asyncio

import pytest

from app.models.chat import AIResponse, ChatMessage, ChatRequest, KnowledgeChunk
from app.services.chat_service import ChatService
from app.services.mock_ticket_service import MockTicketService


class StubAIService:
    async def generate_response(
        self,
        conversation: list[ChatMessage],
        knowledge_context: list[KnowledgeChunk],
    ) -> AIResponse:
        assert conversation[0].content == "What are the store opening procedures?"
        return AIResponse(message="I can help with that.")


def test_chat_service_uses_ai_service() -> None:
    service = ChatService(StubAIService())

    response = asyncio.run(
        service.process_message(
            ChatRequest(message="What are the store opening procedures?", conversation_id="conv-42")
        )
    )

    assert response.conversation_id == "conv-42"
    assert response.message == "I can help with that."
    assert response.status == "success"


def test_chat_service_generates_default_conversation_id() -> None:
    service = ChatService(StubAIService())

    response = asyncio.run(service.process_message(ChatRequest(message="What are the store opening procedures?")))

    assert response.conversation_id.startswith("conversation-")
    assert response.status == "success"


class WorkflowAIService:
    def __init__(self) -> None:
        self.call_count = 0

    async def generate_response(
        self,
        conversation: list[ChatMessage],
        knowledge_context: list[KnowledgeChunk],
    ) -> AIResponse:
        self.call_count += 1
        return AIResponse(message="AI response")


class CountingRetriever:
    def __init__(self) -> None:
        self.call_count = 0

    def retrieve(self, query: str) -> list[KnowledgeChunk]:
        self.call_count += 1
        return []


def test_equipment_fault_requires_confirmation_before_creating_ticket() -> None:
    ticket_service = MockTicketService()
    service = ChatService(WorkflowAIService(), ticket_service=ticket_service)

    first = asyncio.run(service.process_message(ChatRequest(
        message="My coffee machine is broken.",
        conversation_id="conv-ticket",
    )))
    details = asyncio.run(service.process_message(ChatRequest(
        message=("store: Manchester XYZ; machine: Coffee machine; description: "
                 "Not dispensing coffee; safe to use"),
        conversation_id="conv-ticket",
    )))

    assert "please provide" in first.message.lower()
    assert "would you like me to submit this request?" in details.message.lower()
    assert ticket_service.tickets == []

    submitted = asyncio.run(service.process_message(ChatRequest(
        message="confirm",
        conversation_id="conv-ticket",
    )))

    assert "EQ-2026-0001" in submitted.message
    assert len(ticket_service.tickets) == 1


def test_missing_fault_information_is_requested() -> None:
    service = ChatService(WorkflowAIService(), ticket_service=MockTicketService())

    response = asyncio.run(service.process_message(ChatRequest(
        message="My coffee machine is broken.",
        conversation_id="conv-missing",
    )))

    assert "store or location" in response.message
    assert "description of the problem" in response.message
    assert "safe to use" in response.message


def test_natural_multi_turn_fault_details_are_collected_without_repeating_guidance() -> None:
    ticket_service = MockTicketService()
    service = ChatService(WorkflowAIService(), ticket_service=ticket_service)

    first = asyncio.run(service.process_message(ChatRequest(
        message="My coffee machine is broken",
        conversation_id="conv-natural",
    )))
    details = asyncio.run(service.process_message(ChatRequest(
        message=("Manchester XYZ. It's a coffee machine and it isn't dispensing coffee. "
                 "There are no error messages and it is safe to use."),
        conversation_id="conv-natural",
    )))

    assert "Reporting a Fault" in first.message
    assert "store or location" in first.message
    assert "Reporting a Fault" not in details.message
    assert "would you like me to submit this request?" in details.message.lower()
    assert "Manchester XYZ" in details.message
    assert "Coffee machine" in details.message
    assert "isn't dispensing coffee" in details.message
    assert "Safe to use" in details.message
    assert ticket_service.tickets == []


def test_safety_issue_does_not_create_normal_ticket_before_confirmation() -> None:
    ticket_service = MockTicketService()
    service = ChatService(WorkflowAIService(), ticket_service=ticket_service)

    response = asyncio.run(service.process_message(ChatRequest(
        message="The coffee machine is smoking.",
        conversation_id="conv-safety",
    )))

    assert "stop using" in response.message.lower()
    assert "safety escalation" in response.message.lower()
    assert ticket_service.tickets == []


@pytest.mark.parametrize("message", [
    "My coffee machine is broken",
    "The coffee machine isn't working",
    "My coffee machine has a fault",
    "The coffee machine is damaged",
    "Can I report a problem with the coffee machine?",
    "Please raise a ticket for my coffee machine",
    "The coffee machine isn't dispensing coffee",
    "My coffee machine is broken — what should I do?",
])
def test_equipment_fault_trigger_detects_fault_or_action_signals(message: str) -> None:
    assert ChatService._is_equipment_fault(message)


@pytest.mark.parametrize("message", [
    "How do I clean the coffee machine?",
    "What is the reporting procedure for the coffee machine?",
    "How do I use the coffee machine?",
    "What coffee machine do we use?",
])
def test_equipment_fault_trigger_ignores_informational_questions(message: str) -> None:
    assert not ChatService._is_equipment_fault(message)


def test_structured_fault_workflow_precedes_ai_and_clears_after_submission() -> None:
    ticket_service = MockTicketService()
    ai_service = WorkflowAIService()
    retriever = CountingRetriever()
    service = ChatService(ai_service, retriever=retriever, ticket_service=ticket_service)

    initial = asyncio.run(service.process_message(ChatRequest(
        message="My coffee machine has broken",
        conversation_id="conv-structured",
    )))
    details = asyncio.run(service.process_message(ChatRequest(
        message="Store: Manchester Piccadilly, problem: not dispensing coffee, safe to use",
        conversation_id="conv-structured",
    )))
    submitted = asyncio.run(service.process_message(ChatRequest(
        message="Yes, submit it",
        conversation_id="conv-structured",
    )))

    assert "store or location" in initial.message
    assert "Would you like me to submit this request?" in details.message
    assert "Manchester Piccadilly" in details.message
    assert "not dispensing coffee" in details.message
    assert "not dispensing coffee, safe to use" not in details.message
    assert "machine type or identifier" not in details.message
    assert "whether the machine is safe to use" not in details.message
    assert "EQ-2026-0001" in submitted.message
    assert ticket_service.tickets
    assert "conv-structured" not in service.pending_faults
    assert ai_service.call_count == 0
    assert retriever.call_count == 1
