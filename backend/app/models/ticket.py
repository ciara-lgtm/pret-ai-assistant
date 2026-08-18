from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class EquipmentFaultRequest(BaseModel):
    store: str = Field(..., min_length=1)
    equipment: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    safety_status: Literal["safe_to_use", "unsafe_to_use", "unknown"]


class EquipmentFaultTicket(EquipmentFaultRequest):
    ticket_id: str
    ticket_type: Literal["equipment_fault"] = "equipment_fault"
    status: Literal["submitted"] = "submitted"


class PendingEquipmentFault(BaseModel):
    store: str | None = None
    equipment: str | None = None
    description: str | None = None
    safety_status: Literal["safe_to_use", "unsafe_to_use", "unknown"] = "unknown"

    def missing_fields(self) -> list[str]:
        missing = []
        if not self.store:
            missing.append("store or location")
        if not self.equipment:
            missing.append("machine type or identifier")
        if not self.description:
            missing.append("description of the problem")
        if self.safety_status == "unknown":
            missing.append("whether the machine is safe to use")
        return missing