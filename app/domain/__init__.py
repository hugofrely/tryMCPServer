from app.domain.entities import HubSpotContact, HubSpotContactProperties, MatchResult, SyncResult
from app.domain.exceptions import (
    DomainException,
    JobNotFoundError,
    ContactNotFoundError,
    HubSpotApiError,
)
from app.domain.interfaces import (
    CrmClient,
    ContactRepositoryInterface,
    PushJobRepositoryInterface,
    UnitOfWork,
)

__all__ = [
    # Entities
    "HubSpotContact",
    "HubSpotContactProperties",
    "MatchResult",
    "SyncResult",
    # Exceptions
    "DomainException",
    "JobNotFoundError",
    "ContactNotFoundError",
    "HubSpotApiError",
    # Interfaces
    "CrmClient",
    "ContactRepositoryInterface",
    "PushJobRepositoryInterface",
    "UnitOfWork",
]
