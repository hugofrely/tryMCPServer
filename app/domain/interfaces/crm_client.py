from typing import Protocol

from app.domain.entities import HubSpotContact


class CrmClient(Protocol):
    """Interface for CRM client implementations.

    This protocol defines the contract that any CRM client must follow.
    It enables dependency inversion - services depend on this abstraction,
    not on concrete implementations like HubSpotClient.
    """

    def get_all_contacts(self) -> list[HubSpotContact]:
        """Retrieve all contacts from the CRM."""
        ...

    def create_contact(self, contact_data: dict) -> HubSpotContact:
        """Create a new contact in the CRM."""
        ...

    def update_contact(self, contact_id: str, contact_data: dict) -> HubSpotContact:
        """Update an existing contact in the CRM."""
        ...
