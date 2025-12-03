from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PushJobBase(BaseModel):
    """Base schema for PushJob."""

    status: str = "pending"


class PushJobCreate(PushJobBase):
    """Schema for creating a new PushJob."""

    pass


class PushJobUpdate(BaseModel):
    """Schema for updating a PushJob."""

    status: str | None = None
    error: str | None = None
    created_count: int | None = None
    updated_count: int | None = None


class PushJobResponse(PushJobBase):
    """Schema for PushJob response - clean format without SQLAlchemy dependencies."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    error: str | None = None
    created_count: int | None = None
    updated_count: int | None = None
    created_at: datetime
    updated_at: datetime
