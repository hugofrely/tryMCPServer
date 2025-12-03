from fastapi import Depends

from app.dependencies.repositories import (
    get_contact_repository,
    get_push_job_repository,
)
from app.infrastructure import HubSpotClient
from app.repositories import ContactRepository, PushJobRepository
from app.services import PushService
from app.services.contact_matching_service import ContactMatchingService
from app.services.job_executor_service import JobExecutorService, get_job_executor_service

# Singleton instances
_hubspot_client = HubSpotClient()
_matching_service = ContactMatchingService()


def get_hubspot_client() -> HubSpotClient:
    """Dependency that provides the HubSpot client."""
    return _hubspot_client


def get_matching_service() -> ContactMatchingService:
    """Dependency that provides the ContactMatchingService."""
    return _matching_service


def get_push_service(
    push_job_repo: PushJobRepository = Depends(get_push_job_repository),
    contact_repo: ContactRepository = Depends(get_contact_repository),
    hubspot_client: HubSpotClient = Depends(get_hubspot_client),
    matching_service: ContactMatchingService = Depends(get_matching_service),
) -> PushService:
    """Dependency that provides a fully configured PushService."""
    return PushService(
        push_job_repo=push_job_repo,
        contact_repo=contact_repo,
        hubspot_client=hubspot_client,
        matching_service=matching_service,
    )


def get_job_executor() -> JobExecutorService:
    """Dependency that provides the JobExecutorService."""
    return get_job_executor_service()
