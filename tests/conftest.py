from datetime import datetime
from unittest.mock import Mock

import pytest

from app.repositories import ContactRepository, PushJobRepository
from app.schemas import ContactResponse, PushJobResponse
from app.services.contact_matching_service import ContactMatchingService, MatchResult


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
    """Factory to create HubSpot contact dicts."""

    def _make(
        id: str = "hubspot_1",
        email: str | None = None,
        linkedin_id: str | None = None,
        firstname: str | None = None,
        lastname: str | None = None,
    ) -> dict:
        return {
            "id": id,
            "properties": {
                "email": email,
                "linkedin_id": linkedin_id,
                "firstname": firstname,
                "lastname": lastname,
            },
        }

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
def mock_push_job_repo(make_push_job) -> Mock:
    """Mock PushJobRepository."""
    mock = Mock(spec=PushJobRepository)
    mock.create_pending_job.return_value = make_push_job()
    mock.get_by_id.return_value = make_push_job()
    mock.mark_as_completed.return_value = None
    mock.mark_as_failed.return_value = None
    mock.commit.return_value = None
    mock.rollback.return_value = None
    return mock


@pytest.fixture
def mock_contact_repo() -> Mock:
    """Mock ContactRepository."""
    mock = Mock(spec=ContactRepository)
    mock.bulk_create.return_value = []
    mock.get_by_job_id.return_value = []
    mock.update_with_hubspot_data.return_value = None
    return mock


@pytest.fixture
def mock_hubspot_client() -> Mock:
    """Mock HubSpotClient."""
    mock = Mock()
    mock.get_all_contacts.return_value = []
    mock.create_contact.return_value = {"id": "hubspot_new"}
    mock.update_contact.return_value = {"id": "hubspot_1"}
    return mock


@pytest.fixture
def mock_matching_service() -> Mock:
    """Mock ContactMatchingService."""
    mock = Mock(spec=ContactMatchingService)
    mock.match_contacts.return_value = MatchResult(matched=[], unmatched=[])
    return mock
