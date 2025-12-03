from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ContactBase(BaseModel):
    """Base schema for Contact with common fields."""

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    linkedin_id: str | None = None
    phone: str | None = None
    company: str | None = None


class ContactCreate(ContactBase):
    """Schema for creating a new Contact."""

    job_id: int


class ContactUpdate(BaseModel):
    """Schema for updating a Contact."""

    hubspot_id: str | None = None
    status: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    linkedin_id: str | None = None
    phone: str | None = None
    company: str | None = None


class ContactResponse(ContactBase):
    """Schema for Contact response - clean format without SQLAlchemy dependencies."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    hubspot_id: str | None = None
    status: str | None = None
    created_at: datetime
    updated_at: datetime
