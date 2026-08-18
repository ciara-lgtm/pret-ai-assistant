from __future__ import annotations

from typing import Protocol

from app.models.ticket import EquipmentFaultRequest, EquipmentFaultTicket


class TicketService(Protocol):
    """Application boundary for submitting equipment fault requests."""

    def create_equipment_fault(self, request: EquipmentFaultRequest) -> EquipmentFaultTicket:
        """Create and return a submitted equipment fault ticket."""
        ...