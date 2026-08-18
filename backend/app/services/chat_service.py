from __future__ import annotations

import uuid
import re

from app.models.chat import AIResponse, ChatMessage, ChatRequest, ChatResponse, KnowledgeChunk
from app.models.ticket import EquipmentFaultRequest, PendingEquipmentFault
from app.services.ai_service import AIService
from app.services.local_knowledge_retriever import LocalKnowledgeRetriever
from app.services.mock_ticket_service import MockTicketService
from app.services.retriever import Retriever
from app.services.ticket_service import TicketService


class ChatService:
    """Orchestrates chat requests, retrieves relevant knowledge, and delegates AI generation."""

    def __init__(
        self,
        ai_service: AIService,
        retriever: Retriever | None = None,
        ticket_service: TicketService | None = None,
    ) -> None:
        self.ai_service = ai_service
        self.retriever = retriever or LocalKnowledgeRetriever()
        self.ticket_service = ticket_service or MockTicketService()
        self.pending_faults: dict[str, PendingEquipmentFault] = {}

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a user message and return a typed assistant reply."""
        conversation_id = request.conversation_id or f"conversation-{uuid.uuid4()}"

        pending = self.pending_faults.get(conversation_id)
        workflow_message = pending is not None or (
            self._is_equipment_fault(request.message) or self._is_safety_issue(request.message)
        )

        if workflow_message:
            knowledge_context = [] if pending else self.retriever.retrieve(request.message)
            workflow_response = self._process_equipment_fault(
                conversation_id,
                request.message,
                knowledge_context,
            )
            if workflow_response:
                return ChatResponse(
                    message=workflow_response,
                    conversation_id=conversation_id,
                    status="success",
                )

        messages = [
            ChatMessage(role="user", content=request.message),
        ]
        knowledge_context = self.retriever.retrieve(request.message)

        response: AIResponse = await self.ai_service.generate_response(messages, knowledge_context)

        return ChatResponse(
            message=response.message,
            conversation_id=conversation_id,
            status="success",
        )

    def _process_equipment_fault(
        self,
        conversation_id: str,
        message: str,
        knowledge_context: list[KnowledgeChunk],
    ) -> str | None:
        pending = self.pending_faults.get(conversation_id)
        if not pending and not (self._is_equipment_fault(message) or self._is_safety_issue(message)):
            return None

        if not pending:
            pending = PendingEquipmentFault()
            self.pending_faults[conversation_id] = pending
            workflow_started = True
        else:
            workflow_started = False

        self._update_pending_fault(pending, message)

        if self._is_explicit_confirmation(message):
            missing = pending.missing_fields()
            if missing:
                return self._missing_information_response(missing)

            ticket = self.ticket_service.create_equipment_fault(
                EquipmentFaultRequest(
                    store=pending.store,
                    equipment=pending.equipment,
                    description=pending.description,
                    safety_status=pending.safety_status,
                )
            )
            del self.pending_faults[conversation_id]
            return (
                "Your equipment fault request has been submitted. "
                f"Ticket reference: {ticket.ticket_id}."
            )

        missing = pending.missing_fields()
        if missing:
            guidance = self._relevant_reporting_guidance(knowledge_context) if workflow_started else ""
            safety_note = self._safety_note(message, pending)
            return f"{safety_note}{guidance}{self._missing_information_response(missing)}"

        return self._confirmation_response(pending)

    @staticmethod
    def _is_equipment_fault(message: str) -> bool:
        value = message.lower()
        return any(signal in value for signal in (
            "broken",
            "not working",
            "isn't working",
            "fault",
            "damaged",
            "problem with",
            "issue with",
            "isn't dispensing",
            "not dispensing",
            "leaking",
            "report a problem",
            "report an issue",
            "raise a ticket",
            "submit a ticket",
            "create a ticket",
        ))

    @staticmethod
    def _is_safety_issue(message: str) -> bool:
        value = message.lower()
        return any(term in value for term in (
            "smoking",
            "smoke",
            "sparks",
            "burning smell",
            "exposed wiring",
            "electrical noise",
            "electrical sound",
        ))

    @staticmethod
    def _is_explicit_confirmation(message: str) -> bool:
        normalized = re.sub(r"[.!?]+$", "", message.strip().lower())
        return normalized in {
            "yes",
            "confirm",
            "submit it",
            "raise the request",
            "yes submit it",
            "yes, submit it",
        }

    @staticmethod
    def _update_pending_fault(pending: PendingEquipmentFault, message: str) -> None:
        value = message.strip()
        lowered = value.lower()
        if ChatService._is_safety_issue(value):
            pending.safety_status = "unsafe_to_use"
        elif any(term in lowered for term in ("safe to use", "can be used safely", "usable")):
            pending.safety_status = "safe_to_use"
        elif any(term in lowered for term in ("unsafe to use", "not safe", "cannot be used safely")):
            pending.safety_status = "unsafe_to_use"

        store_match = re.search(r"(?:store|location)\s*[:=-]\s*([^,;\n]+)", value, re.IGNORECASE)
        if store_match:
            pending.store = store_match.group(1).strip()

        equipment_match = re.search(
            r"(?:machine|equipment)\s*(?:type|identifier|id)?\s*[:=-]\s*([^,;\n]+)",
            value,
            re.IGNORECASE,
        )
        if equipment_match:
            pending.equipment = equipment_match.group(1).strip()
        elif "coffee machine" in lowered:
            pending.equipment = "Coffee machine"

        description_match = re.search(
            r"(?:description|problem)\s*[:=-]\s*(.*?)(?=,\s*(?:safe|unsafe)\s+to\s+use\b|;|\n|$)",
            value,
            re.IGNORECASE,
        )
        if description_match:
            pending.description = description_match.group(1).strip()
        elif not pending.description and not ChatService._is_explicit_confirmation(value):
            if pending.store is None:
                pending.store = ChatService._natural_store(value)

            if pending.equipment is None and "coffee machine" in lowered:
                pending.equipment = "Coffee machine"

            if pending.description is None:
                description = ChatService._natural_description(value)
                if description and not (
                    ChatService._is_equipment_fault(value) and len(value.split()) <= 5
                ):
                    pending.description = description

    @staticmethod
    def _missing_information_response(missing: list[str]) -> str:
        return "To prepare the request, please provide: " + ", ".join(missing) + "."

    @staticmethod
    def _natural_store(message: str) -> str | None:
        """Use a leading standalone sentence as a conversational store/location value."""
        first_sentence = re.split(r"[.!?]", message, maxsplit=1)[0].strip(" ,")
        lowered = first_sentence.lower()
        if not first_sentence or any(term in lowered for term in (
            "machine",
            "equipment",
            "broken",
            "safe",
            "smoke",
            "spark",
            "error",
        )):
            return None
        return first_sentence

    @staticmethod
    def _natural_description(message: str) -> str | None:
        match = re.search(
            r"(?:it|machine|equipment)\s+(?:isn't|is not|is|was|has)\s+([^.!?]+)",
            message,
            re.IGNORECASE,
        )
        if match:
            description = match.group(0).strip()
            if "safe to use" not in description.lower():
                return description
        return None

    @staticmethod
    def _confirmation_response(pending: PendingEquipmentFault) -> str:
        safety_status = {
            "safe_to_use": "Safe to use",
            "unsafe_to_use": "Unsafe to use",
            "unknown": "Unknown",
        }[pending.safety_status]
        return (
            "I have the details for this equipment fault request:\n"
            f"- Store: {pending.store}\n"
            f"- Equipment: {pending.equipment}\n"
            f"- Problem: {pending.description}\n"
            f"- Safety status: {safety_status}\n\n"
            "Would you like me to submit this request?"
        )

    @staticmethod
    def _safety_note(message: str, pending: PendingEquipmentFault) -> str:
        if pending.safety_status == "unsafe_to_use" and ChatService._is_safety_issue(message):
            return (
                "This may be an immediate safety concern. Stop using the equipment and "
                "follow the Equipment Safety Escalation procedure.\n\n"
            )
        return ""

    @staticmethod
    def _relevant_reporting_guidance(knowledge_context: list[KnowledgeChunk]) -> str:
        for chunk in knowledge_context:
            if "reporting a fault" in chunk.content.lower():
                return f"Here is the relevant reporting guidance:\n{chunk.content}\n\n"
        return ""
