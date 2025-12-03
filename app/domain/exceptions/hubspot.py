from app.domain.exceptions.base import DomainException


class HubSpotApiError(DomainException):
    """Raised when there's an error communicating with HubSpot API."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(f"HubSpot API error: {message}")
