from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from app.async_task_executor import AsyncTaskExecutor
from app.database import Session, engine
from app.dependencies import get_push_service
from app.dependencies.repositories import (
    create_contact_repository,
    create_push_job_repository,
)
from app.dependencies.services import get_hubspot_client, get_matching_service
from app.models import Base
from app.services import PushService

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CRM Push API")

task_executor = AsyncTaskExecutor()
task_executor.add_task(
    "process_push_job",
    lambda job_id: _process_push_job(job_id),
)


class ProfileSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    linkedin_id: str | None = None
    phone: str | None = None
    company: str | None = None


class PushRequestSchema(BaseModel):
    profiles: list[ProfileSchema]


def _process_push_job(job_id: str) -> None:
    """Background task to process a push job (runs outside request context)."""
    with Session() as session:
        service = PushService(
            push_job_repo=create_push_job_repository(session),
            contact_repo=create_contact_repository(session),
            hubspot_client=get_hubspot_client(),
            matching_service=get_matching_service(),
        )
        service.process_job(int(job_id))


@app.post("/push")
async def push_profiles(
    request: PushRequestSchema,
    service: PushService = Depends(get_push_service),
):
    """Create a new push job with the provided profiles."""
    push_job = service.create_push_job(
        [profile.model_dump() for profile in request.profiles]
    )
    job_id = str(push_job.id)

    task_executor.execute("process_push_job", job_id)
    return {"job_id": job_id}


@app.get("/push/{job_id}")
async def get_push_status(
    job_id: str,
    service: PushService = Depends(get_push_service),
):
    """Get the status of a push job."""
    job = service.get_job_status(int(job_id))

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id": job_id,
        "status": job.status,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }

    if job.status == "completed":
        response["created"] = job.created_count or 0
        response["updated"] = job.updated_count or 0
    elif job.status == "failed":
        response["error"] = job.error or "Unknown error"

    return response


@app.get("/health")
async def health():
    return {"status": "ok"}
