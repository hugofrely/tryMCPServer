from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_session
from app.repositories import ContactRepository, PushJobRepository


def get_contact_repository(
    session: Session = Depends(get_session),
) -> ContactRepository:
    """Dependency that provides a ContactRepository instance."""
    return ContactRepository(session)


def get_push_job_repository(
    session: Session = Depends(get_session),
) -> PushJobRepository:
    """Dependency that provides a PushJobRepository instance."""
    return PushJobRepository(session)


# Factory functions for manual instantiation (background tasks)
def create_contact_repository(session: Session) -> ContactRepository:
    """Create a ContactRepository with a provided session (for background tasks)."""
    return ContactRepository(session)


def create_push_job_repository(session: Session) -> PushJobRepository:
    """Create a PushJobRepository with a provided session (for background tasks)."""
    return PushJobRepository(session)
