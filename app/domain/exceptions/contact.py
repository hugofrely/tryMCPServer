from app.domain.exceptions.base import DomainException


class ContactNotFoundError(DomainException):
    """Raised when a contact is not found."""

    def __init__(self, contact_id: str):
        self.contact_id = contact_id
        super().__init__(f"Contact with id '{contact_id}' not found")
