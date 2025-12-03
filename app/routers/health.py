from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the API is running correctly.",
)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")
