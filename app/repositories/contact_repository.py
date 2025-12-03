from sqlalchemy.orm import Session

from app.models import Contact
from app.repositories.base import BaseRepository
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate


class ContactRepository(BaseRepository[Contact, ContactCreate, ContactUpdate, ContactResponse]):
    """
    Repository for Contact operations.

    Provides clean data access layer for Contact entities,
    returning Pydantic models instead of SQLAlchemy objects.
    """

    def __init__(self, session: Session):
        super().__init__(session)

    @property
    def _model(self) -> type[Contact]:
        return Contact

    @property
    def _response_schema(self) -> type[ContactResponse]:
        return ContactResponse

    def get_by_job_id(self, job_id: int) -> list[ContactResponse]:
        """Get all contacts for a specific job."""
        db_objs = (
            self._session.query(self._model)
            .filter(self._model.job_id == job_id)
            .all()
        )
        return self._to_response_list(db_objs)

    def get_by_email(self, email: str) -> ContactResponse | None:
        """Get a contact by email."""
        db_obj = (
            self._session.query(self._model)
            .filter(self._model.email == email)
            .first()
        )
        return self._to_response(db_obj)

    def get_by_linkedin_id(self, linkedin_id: str) -> ContactResponse | None:
        """Get a contact by LinkedIn ID."""
        db_obj = (
            self._session.query(self._model)
            .filter(self._model.linkedin_id == linkedin_id)
            .first()
        )
        return self._to_response(db_obj)

    def get_synced_contacts_by_job_id(self, job_id: int) -> list[ContactResponse]:
        """Get all contacts for a job that have been synced to HubSpot."""
        db_objs = (
            self._session.query(self._model)
            .filter(
                self._model.job_id == job_id,
                self._model.hubspot_id.isnot(None)
            )
            .all()
        )
        return self._to_response_list(db_objs)

    def mark_as_completed(self, contact_id: int, hubspot_id: str) -> ContactResponse | None:
        """Mark a contact as completed with HubSpot ID."""
        return self.update(
            contact_id,
            ContactUpdate(status="completed", hubspot_id=hubspot_id)
        )

    def mark_as_failed(self, contact_id: int, error: str | None = None) -> ContactResponse | None:
        """Mark a contact as failed."""
        return self.update(contact_id, ContactUpdate(status="failed"))

    def bulk_create(self, schemas: list[ContactCreate]) -> list[ContactResponse]:
        """Create multiple contacts at once."""
        db_objs = [self._model(**schema.model_dump()) for schema in schemas]
        self._session.add_all(db_objs)
        self._session.flush()
        for obj in db_objs:
            self._session.refresh(obj)
        return self._to_response_list(db_objs)

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
        return self.update(
            contact_id,
            ContactUpdate(
                hubspot_id=hubspot_id,
                status="completed",
                first_name=first_name,
                last_name=last_name,
                email=email,
                linkedin_id=linkedin_id,
                phone=phone,
                company=company,
            )
        )
