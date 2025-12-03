from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response DTO."""

    detail: str = Field(
        ...,
        description="Error description",
    )
