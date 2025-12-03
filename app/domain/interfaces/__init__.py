from app.domain.interfaces.crm_client import CrmClient
from app.domain.interfaces.repositories import ContactRepositoryInterface, PushJobRepositoryInterface
from app.domain.interfaces.unit_of_work import UnitOfWork

__all__ = [
    "CrmClient",
    "ContactRepositoryInterface",
    "PushJobRepositoryInterface",
    "UnitOfWork",
]
