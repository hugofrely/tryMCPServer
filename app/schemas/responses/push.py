from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.enums import JobStatus


class PushJobCreatedResponse(BaseModel):
    """Response DTO when a push job is created."""

    job_id: str = Field(
        ...,
        description="Unique identifier of the created job",
        examples=["123"],
    )
    message: str = Field(
        default="Job created successfully",
        description="Status message",
    )


class PushJobStatusResponse(BaseModel):
    """Response DTO for push job status."""

    job_id: str = Field(
        ...,
        description="Unique identifier of the job",
    )
    status: JobStatus = Field(
        ...,
        description="Current status of the job",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp when the job was created",
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Timestamp when the job was last updated",
    )
    created_count: int | None = Field(
        default=None,
        description="Number of contacts created in HubSpot (only when completed)",
    )
    updated_count: int | None = Field(
        default=None,
        description="Number of contacts updated in HubSpot (only when completed)",
    )
    error: str | None = Field(
        default=None,
        description="Error message (only when failed)",
    )
