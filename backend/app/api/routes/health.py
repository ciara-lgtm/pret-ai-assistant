from fastapi import APIRouter

from app.models.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def read_health() -> HealthResponse:
    """Return a system health report for the backend service."""
    return HealthService.get_health()


@router.get("/api/health", response_model=HealthResponse, include_in_schema=False)
def read_health_alias() -> HealthResponse:
    """Backward-compatible health alias for API-prefixed clients."""
    return HealthService.get_health()
