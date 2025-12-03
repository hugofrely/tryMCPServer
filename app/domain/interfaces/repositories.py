from typing import Protocol

from app.schemas import ContactCreate, ContactResponse, ContactUpdate
from app.schemas import PushJobCreate, PushJobResponse, PushJobUpdate


class ContactRepositoryInterface(Protocol):
    """Interface for contact repository implementations."""

    def get_by_id(self, id: int) -> ContactResponse | None:
        """Get a contact by ID."""
        ...

    def get_by_job_id(self, job_id: int) -> list[ContactResponse]:
        """Get all contacts for a specific job."""
        ...

    def create(self, schema: ContactCreate) -> ContactResponse:
        """Create a new contact."""
        ...

    def update(self, id: int, schema: ContactUpdate) -> ContactResponse | None:
        """Update a contact."""
        ...

    def bulk_create(self, schemas: list[ContactCreate]) -> list[ContactResponse]:
        """Create multiple contacts at once."""
        ...

    def update_with_hubspot_data(
        self,
        contact_id: int,
        hubspot_id: str,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        linkedin_id: str | None = None,
        phone: str | None = None,
        company: str | None = None,
    ) -> ContactResponse | None:
        """Update contact with data from HubSpot sync."""
        ...


class PushJobRepositoryInterface(Protocol):
    """Interface for push job repository implementations."""

    def get_by_id(self, id: int) -> PushJobResponse | None:
        """Get a job by ID."""
        ...

    def create(self, schema: PushJobCreate) -> PushJobResponse:
        """Create a new job."""
        ...

    def create_pending_job(self) -> PushJobResponse:
        """Create a new pending job."""
        ...

    def mark_as_completed(
        self,
        job_id: int,
        created_count: int = 0,
        updated_count: int = 0,
    ) -> PushJobResponse | None:
        """Mark a job as completed with counts."""
        ...

    def mark_as_failed(self, job_id: int, error: str) -> PushJobResponse | None:
        """Mark a job as failed with error message."""
        ...
