from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database import Session as SessionFactory


def get_session() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields a session and ensures it's closed after the request.
    """
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
