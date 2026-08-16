from __future__ import annotations

from app.models.health import HealthResponse


class HealthService:
    """Service responsible for readiness and health-check responses."""

    @staticmethod
    def get_health() -> HealthResponse:
        """Return a simple application health response."""
        return HealthResponse(status="ok", service="pret-ai-assistant")
