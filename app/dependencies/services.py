from app.domain import CrmClient, UnitOfWork
from app.infrastructure import HubSpotClient, SqlAlchemyUnitOfWork
from app.services import PushService
from app.services.contact_matching_service import ContactMatchingService
from app.services.job_executor_service import JobExecutorService, get_job_executor_service

# Singleton instances
_hubspot_client: CrmClient = HubSpotClient()
_matching_service = ContactMatchingService()


def get_crm_client() -> CrmClient:
    """Dependency that provides the CRM client (HubSpot implementation)."""
    return _hubspot_client


def get_matching_service() -> ContactMatchingService:
    """Dependency that provides the ContactMatchingService."""
    return _matching_service


def get_unit_of_work() -> UnitOfWork:
    """Dependency that provides a new UnitOfWork instance."""
    return SqlAlchemyUnitOfWork()


def get_push_service() -> PushService:
    """Dependency that provides a fully configured PushService."""
    return PushService(
        uow=get_unit_of_work(),
        crm_client=get_crm_client(),
        matching_service=get_matching_service(),
    )


def get_job_executor() -> JobExecutorService:
    """Dependency that provides the JobExecutorService."""
    return get_job_executor_service()
