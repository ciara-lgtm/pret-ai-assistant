from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Standard health response model for the service."""

    status: str = Field(default="ok", description="Current application health state.")
    service: str = Field(default="pret-ai-assistant", description="Name of the backend service.")
