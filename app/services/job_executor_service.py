from app.async_task_executor import AsyncTaskExecutor
from app.database import Session


class JobExecutorService:
    """
    Service responsible for scheduling and executing background jobs.

    This service abstracts the job execution infrastructure from the rest
    of the application, following the Single Responsibility Principle.
    """

    def __init__(self, task_executor: AsyncTaskExecutor | None = None):
        self._executor = task_executor or AsyncTaskExecutor()
        self._register_tasks()

    def _register_tasks(self) -> None:
        """Register all background task handlers."""
        self._executor.add_task("process_push_job", self._process_push_job)

    def _process_push_job(self, job_id: str) -> None:
        """Execute push job processing in background."""
        # Import inside method to avoid circular imports
        from app.dependencies.repositories import (
            create_contact_repository,
            create_push_job_repository,
        )
        from app.dependencies.services import get_hubspot_client, get_matching_service
        from app.services.push_service import PushService

        with Session() as session:
            service = PushService(
                push_job_repo=create_push_job_repository(session),
                contact_repo=create_contact_repository(session),
                hubspot_client=get_hubspot_client(),
                matching_service=get_matching_service(),
            )
            service.process_job(int(job_id))

    def schedule_push_job(self, job_id: int) -> None:
        """
        Schedule a push job for background execution.

        Args:
            job_id: The ID of the job to process.
        """
        self._executor.execute("process_push_job", str(job_id))


# Singleton instance
_job_executor_service: JobExecutorService | None = None


def get_job_executor_service() -> JobExecutorService:
    """Get or create the singleton JobExecutorService instance."""
    global _job_executor_service
    if _job_executor_service is None:
        _job_executor_service = JobExecutorService()
    return _job_executor_service
