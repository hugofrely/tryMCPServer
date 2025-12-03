from app.domain.exceptions.base import DomainException


class JobNotFoundError(DomainException):
    """Raised when a job is not found."""

    def __init__(self, job_id: int):
        self.job_id = job_id
        super().__init__(f"Job with id '{job_id}' not found")
