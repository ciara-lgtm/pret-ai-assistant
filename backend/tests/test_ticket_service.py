from app.models.ticket import EquipmentFaultRequest
from app.services.mock_ticket_service import MockTicketService


def test_mock_ticket_service_generates_predictable_ticket_ids() -> None:
    service = MockTicketService()
    request = EquipmentFaultRequest(
        store="Manchester XYZ",
        equipment="Coffee machine",
        description="Not dispensing coffee",
        safety_status="safe_to_use",
    )

    first = service.create_equipment_fault(request)
    second = service.create_equipment_fault(request)

    assert first.ticket_id == "EQ-2026-0001"
    assert second.ticket_id == "EQ-2026-0002"
    assert first.status == "submitted"
    assert len(service.tickets) == 2