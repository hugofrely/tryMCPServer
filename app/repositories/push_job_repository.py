from datetime import datetime

from sqlalchemy.orm import Session

from app.infrastructure import PushJob
from app.repositories.base import BaseRepository
from app.schemas.push_job import PushJobCreate, PushJobResponse, PushJobUpdate


class PushJobRepository(BaseRepository[PushJob, PushJobCreate, PushJobUpdate, PushJobResponse]):
    """
    Repository for PushJob operations.

    Provides clean data access layer for PushJob entities,
    returning Pydantic models instead of SQLAlchemy objects.
    """

    def __init__(self, session: Session):
        super().__init__(session)

    @property
    def _model(self) -> type[PushJob]:
        return PushJob

    @property
    def _response_schema(self) -> type[PushJobResponse]:
        return PushJobResponse

    def get_by_status(self, status: str) -> list[PushJobResponse]:
        """Get all jobs with a specific status."""
        db_objs = (
            self._session.query(self._model)
            .filter(self._model.status == status)
            .all()
        )
        return self._to_response_list(db_objs)

    def get_pending_jobs(self) -> list[PushJobResponse]:
        """Get all pending jobs."""
        return self.get_by_status("pending")

    def get_completed_jobs(self) -> list[PushJobResponse]:
        """Get all completed jobs."""
        return self.get_by_status("completed")

    def get_failed_jobs(self) -> list[PushJobResponse]:
        """Get all failed jobs."""
        return self.get_by_status("failed")

    def mark_as_completed(
        self,
        job_id: int,
        created_count: int = 0,
        updated_count: int = 0
    ) -> PushJobResponse | None:
        """Mark a job as completed with counts."""
        db_obj = self._session.query(self._model).filter(self._model.id == job_id).first()
        if db_obj is None:
            return None

        db_obj.status = "completed"
        db_obj.created_count = created_count
        db_obj.updated_count = updated_count
        db_obj.updated_at = datetime.now()

        self._session.flush()
        self._session.refresh(db_obj)
        return self._to_response(db_obj)

    def mark_as_failed(self, job_id: int, error: str) -> PushJobResponse | None:
        """Mark a job as failed with error message."""
        db_obj = self._session.query(self._model).filter(self._model.id == job_id).first()
        if db_obj is None:
            return None

        db_obj.status = "failed"
        db_obj.error = error
        db_obj.updated_at = datetime.now()

        self._session.flush()
        self._session.refresh(db_obj)
        return self._to_response(db_obj)

    def create_pending_job(self) -> PushJobResponse:
        """Create a new pending job."""
        return self.create(PushJobCreate(status="pending"))
