from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response DTO for health check."""

    status: str = Field(
        default="ok",
        description="Health status",
    )
