from datetime import datetime
from unittest.mock import Mock

import pytest

from app.domain import HubSpotContact, HubSpotContactProperties, MatchResult
from app.schemas import ContactResponse, PushJobResponse
from app.services.contact_matching_service import ContactMatchingService


# =============================================================================
# Factories
# =============================================================================


@pytest.fixture
def make_contact():
    """Factory to create ContactResponse objects."""

    def _make(
        id: int = 1,
        job_id: int = 1,
        email: str | None = None,
        linkedin_id: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        hubspot_id: str | None = None,
        status: str = "pending",
    ) -> ContactResponse:
        return ContactResponse(
            id=id,
            job_id=job_id,
            hubspot_id=hubspot_id,
            status=status,
            first_name=first_name,
            last_name=last_name,
            email=email,
            linkedin_id=linkedin_id,
            phone=None,
            company=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    return _make


@pytest.fixture
def make_hubspot_contact():
    """Factory to create HubSpotContact domain objects."""

    def _make(
        id: str = "hubspot_1",
        email: str | None = None,
        linkedin_id: str | None = None,
        firstname: str | None = None,
        lastname: str | None = None,
        phone: str | None = None,
        company: str | None = None,
    ) -> HubSpotContact:
        return HubSpotContact(
            id=id,
            properties=HubSpotContactProperties(
                email=email,
                linkedin_id=linkedin_id,
                firstname=firstname,
                lastname=lastname,
                phone=phone,
                company=company,
            ),
        )

    return _make


@pytest.fixture
def make_push_job():
    """Factory to create PushJobResponse objects."""

    def _make(
        id: int = 1,
        status: str = "pending",
        error: str | None = None,
        created_count: int = 0,
        updated_count: int = 0,
    ) -> PushJobResponse:
        return PushJobResponse(
            id=id,
            status=status,
            error=error,
            created_count=created_count,
            updated_count=updated_count,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    return _make


# =============================================================================
# Mocks
# =============================================================================


@pytest.fixture
def mock_uow(make_push_job) -> Mock:
    """Mock UnitOfWork with push_jobs and contacts repositories."""
    mock = Mock()

    # Mock push_jobs repository
    mock.push_jobs = Mock()
    mock.push_jobs.create_pending_job.return_value = make_push_job()
    mock.push_jobs.get_by_id.return_value = make_push_job()
    mock.push_jobs.mark_as_completed.return_value = None
    mock.push_jobs.mark_as_failed.return_value = None

    # Mock contacts repository
    mock.contacts = Mock()
    mock.contacts.bulk_create.return_value = []
    mock.contacts.get_by_job_id.return_value = []
    mock.contacts.update_with_hubspot_data.return_value = None

    # Context manager support
    mock.__enter__ = Mock(return_value=mock)
    mock.__exit__ = Mock(return_value=None)

    return mock


@pytest.fixture
def mock_crm_client(make_hubspot_contact) -> Mock:
    """Mock CRM client (HubSpot implementation)."""
    mock = Mock()
    mock.get_all_contacts.return_value = []
    mock.create_contact.return_value = make_hubspot_contact(id="hubspot_new")
    mock.update_contact.return_value = make_hubspot_contact(id="hubspot_1")
    return mock


@pytest.fixture
def mock_matching_service() -> Mock:
    """Mock ContactMatchingService."""
    mock = Mock(spec=ContactMatchingService)
    mock.match_contacts.return_value = MatchResult(matched=[], unmatched=[])
    return mock
