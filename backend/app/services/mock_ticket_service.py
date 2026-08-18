from __future__ import annotations

from app.models.ticket import EquipmentFaultRequest, EquipmentFaultTicket


class MockTicketService:
    """In-memory ticket action for the proof of concept."""

    def __init__(self) -> None:
        self.tickets: list[EquipmentFaultTicket] = []

    def create_equipment_fault(self, request: EquipmentFaultRequest) -> EquipmentFaultTicket:
        ticket = EquipmentFaultTicket(
            **request.model_dump(),
            ticket_id=f"EQ-2026-{len(self.tickets) + 1:04d}",
        )
        self.tickets.append(ticket)
        return ticket