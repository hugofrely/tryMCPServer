from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.dependencies import get_job_executor, get_push_service
from app.schemas import (
    ErrorResponse,
    JobStatus,
    PushJobCreatedResponse,
    PushJobStatusResponse,
    PushProfilesRequest,
)
from app.services import JobExecutorService, PushService

router = APIRouter(prefix="/push", tags=["Push"])


# Type aliases for dependency injection
PushServiceDep = Annotated[PushService, Depends(get_push_service)]
JobExecutorDep = Annotated[JobExecutorService, Depends(get_job_executor)]


@router.post(
    "",
    response_model=PushJobCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Push profiles to HubSpot",
    description="Create a new push job to sync profiles with HubSpot CRM.",
    responses={
        201: {"description": "Job created successfully"},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
)
async def push_profiles(
    request: PushProfilesRequest,
    service: PushServiceDep,
    job_executor: JobExecutorDep,
) -> PushJobCreatedResponse:
    """
    Push profiles to HubSpot.

    This endpoint creates a background job that will:
    1. Match profiles with existing HubSpot contacts
    2. Update matched contacts
    3. Create new contacts for unmatched profiles
    """
    push_job = service.create_push_job(
        [profile.model_dump() for profile in request.profiles]
    )

    job_executor.schedule_push_job(push_job.id)

    return PushJobCreatedResponse(
        job_id=str(push_job.id),
        message="Job created successfully",
    )


@router.get(
    "/{job_id}",
    response_model=PushJobStatusResponse,
    summary="Get push job status",
    description="Get the current status of a push job.",
    responses={
        200: {"description": "Job status retrieved successfully"},
        404: {"description": "Job not found", "model": ErrorResponse},
    },
)
async def get_push_status(
    job_id: Annotated[
        str,
        Path(
            description="The unique identifier of the push job",
            examples=["123"],
        ),
    ],
    service: PushServiceDep,
) -> PushJobStatusResponse:
    """Get the status of a push job."""
    try:
        job_id_int = int(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job_id format. Must be a valid integer.",
        )

    job = service.get_job_status(job_id_int)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id '{job_id}' not found",
        )

    return PushJobStatusResponse(
        job_id=job_id,
        status=JobStatus(job.status),
        created_at=job.created_at,
        updated_at=job.updated_at,
        created_count=job.created_count if job.status == "completed" else None,
        updated_count=job.updated_count if job.status == "completed" else None,
        error=job.error if job.status == "failed" else None,
    )
