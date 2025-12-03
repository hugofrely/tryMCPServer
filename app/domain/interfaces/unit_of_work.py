from typing import Protocol

from app.domain.interfaces.repositories import (
    ContactRepositoryInterface,
    PushJobRepositoryInterface,
)


class UnitOfWork(Protocol):
    """
    Unit of Work pattern interface.

    Manages transactions and provides access to repositories.
    This abstraction hides database-specific concepts (commit, rollback)
    from the service layer.

    Usage:
        with uow:
            uow.push_jobs.create_pending_job()
            uow.contacts.bulk_create(contacts)
            # Auto-commits on successful exit
            # Auto-rollbacks on exception
    """

    push_jobs: PushJobRepositoryInterface
    contacts: ContactRepositoryInterface

    def __enter__(self) -> "UnitOfWork":
        """Enter the context manager."""
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager, handling commit/rollback."""
        ...
