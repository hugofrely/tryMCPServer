from app.domain import (
    CrmClient,
    HubSpotContact,
    JobNotFoundError,
    SyncResult,
    UnitOfWork,
)
from app.schemas import ContactCreate, ContactResponse, PushJobResponse
from app.services.contact_matching_service import ContactMatchingService


class PushService:
    """
    Service responsible for orchestrating the push of contacts to HubSpot.

    This service handles:
    - Creating push jobs and contacts
    - Syncing contacts with HubSpot (matching, creating, updating)
    - Updating job status

    Dependencies are injected through the constructor using interfaces (Protocol),
    following the Dependency Inversion Principle.

    Transaction management is handled by the UnitOfWork, keeping database-specific
    concerns out of the service layer.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        crm_client: CrmClient,
        matching_service: ContactMatchingService,
    ):
        self._uow = uow
        self._crm_client = crm_client
        self._matching_service = matching_service

    def create_push_job(self, profiles: list[dict]) -> PushJobResponse:
        """
        Create a new push job with associated contacts.

        Args:
            profiles: List of profile dictionaries containing contact data.

        Returns:
            The created PushJob.
        """
        with self._uow:
            push_job = self._uow.push_jobs.create_pending_job()

            contact_schemas = [
                ContactCreate(
                    job_id=push_job.id,
                    first_name=profile.get("first_name"),
                    last_name=profile.get("last_name"),
                    email=profile.get("email"),
                    linkedin_id=profile.get("linkedin_id"),
                    phone=profile.get("phone"),
                    company=profile.get("company"),
                )
                for profile in profiles
            ]
            self._uow.contacts.bulk_create(contact_schemas)

            return push_job

    def process_job(self, job_id: int) -> SyncResult:
        """
        Process a push job by syncing all its contacts with HubSpot.

        Args:
            job_id: The ID of the job to process.

        Returns:
            SyncResult with counts of created and updated contacts.

        Raises:
            JobNotFoundError: If the job is not found.
        """
        with self._uow:
            push_job = self._uow.push_jobs.get_by_id(job_id)
            if not push_job:
                raise JobNotFoundError(job_id)

            try:
                result = self._sync_contacts(job_id)

                self._uow.push_jobs.mark_as_completed(
                    job_id=job_id,
                    created_count=result.created_count,
                    updated_count=result.updated_count,
                )

                return result

            except Exception as exc:
                # UnitOfWork will rollback automatically on exception
                # We need a new transaction to mark the job as failed
                error = exc

        # Mark as failed in a separate transaction
        with self._uow:
            self._uow.push_jobs.mark_as_failed(job_id, str(error))

        raise error

    def get_job_status(self, job_id: int) -> PushJobResponse:
        """
        Get the status of a push job.

        Args:
            job_id: The ID of the job.

        Returns:
            The job status response.

        Raises:
            JobNotFoundError: If the job is not found.
        """
        with self._uow:
            job = self._uow.push_jobs.get_by_id(job_id)
            if not job:
                raise JobNotFoundError(job_id)
            return job

    def _sync_contacts(self, job_id: int) -> SyncResult:
        """Sync all contacts for a job with HubSpot."""
        job_contacts = self._uow.contacts.get_by_job_id(job_id)
        hubspot_contacts = self._crm_client.get_all_contacts()

        match_result = self._matching_service.match_contacts(
            local_contacts=job_contacts,
            hubspot_contacts=hubspot_contacts,
        )

        updated_count = self._update_matched_contacts(match_result.matched)
        created_count = self._create_new_contacts(match_result.unmatched)

        return SyncResult(created_count=created_count, updated_count=updated_count)

    def _update_matched_contacts(
        self,
        matched_contacts: list[tuple[ContactResponse, HubSpotContact]],
    ) -> int:
        """Update contacts that matched with existing HubSpot contacts."""
        updated_count = 0

        for local_contact, hubspot_contact in matched_contacts:
            contact_data = self._merge_contact_data(local_contact, hubspot_contact)

            self._crm_client.update_contact(hubspot_contact.id, contact_data)

            self._uow.contacts.update_with_hubspot_data(
                contact_id=local_contact.id,
                hubspot_id=hubspot_contact.id,
                **contact_data,
            )
            updated_count += 1

        return updated_count

    def _create_new_contacts(
        self,
        unmatched_contacts: list[ContactResponse],
    ) -> int:
        """Create new contacts in HubSpot for unmatched local contacts."""
        created_count = 0

        for local_contact in unmatched_contacts:
            contact_data = {
                "first_name": local_contact.first_name,
                "last_name": local_contact.last_name,
                "email": local_contact.email,
                "linkedin_id": local_contact.linkedin_id,
                "phone": local_contact.phone,
                "company": local_contact.company,
            }

            hubspot_contact = self._crm_client.create_contact(contact_data)

            self._uow.contacts.update_with_hubspot_data(
                contact_id=local_contact.id,
                hubspot_id=hubspot_contact.id,
                **contact_data,
            )
            created_count += 1

        return created_count

    def _merge_contact_data(
        self,
        local_contact: ContactResponse,
        hubspot_contact: HubSpotContact,
    ) -> dict:
        """Merge local contact data with HubSpot contact data (local takes priority)."""
        props = hubspot_contact.properties

        return {
            "first_name": local_contact.first_name or props.firstname,
            "last_name": local_contact.last_name or props.lastname,
            "email": local_contact.email or props.email,
            "linkedin_id": local_contact.linkedin_id or props.linkedin_id,
            "phone": local_contact.phone or props.phone,
            "company": local_contact.company or props.company,
        }
