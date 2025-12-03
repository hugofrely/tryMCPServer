from sqlalchemy.orm import Session

from app.infrastructure.database.connection import Session as SessionFactory


class SqlAlchemyUnitOfWork:
    """
    SQLAlchemy implementation of the Unit of Work pattern.

    Manages database transactions and provides access to repositories.
    Automatically commits on successful context exit, rolls back on exception.
    """

    def __init__(self, session_factory: type[Session] = SessionFactory):
        self._session_factory = session_factory
        self._session: Session | None = None

    @property
    def push_jobs(self):
        """Access to push job repository."""
        # Import here to avoid circular imports
        from app.repositories import PushJobRepository

        if self._session is None:
            raise RuntimeError("UnitOfWork not started. Use 'with' statement.")
        return PushJobRepository(self._session)

    @property
    def contacts(self):
        """Access to contact repository."""
        # Import here to avoid circular imports
        from app.repositories import ContactRepository

        if self._session is None:
            raise RuntimeError("UnitOfWork not started. Use 'with' statement.")
        return ContactRepository(self._session)

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        """Start a new transaction."""
        self._session = self._session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """End the transaction - commit on success, rollback on exception."""
        if self._session is None:
            return

        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
        finally:
            self._session.close()
            self._session = None
