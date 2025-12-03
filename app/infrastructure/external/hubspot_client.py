"""
Mocked HubSpot API client.
In a real scenario, this would make actual HTTP requests to HubSpot API.

This implementation conforms to the CrmClient protocol defined in the domain layer.
"""

from app.domain import HubSpotContact, HubSpotContactProperties, ContactNotFoundError


class HubSpotClient:
    """
    HubSpot CRM client implementation.

    Implements the CrmClient protocol for dependency inversion.
    """

    def __init__(self):
        self._contacts: dict[str, HubSpotContact] = {
            "hubspot_1": HubSpotContact(
                id="hubspot_1",
                properties=HubSpotContactProperties(
                    firstname="John",
                    lastname="Doe",
                    email="john.doe@example.com",
                    linkedin_id="linkedin_1",
                    phone="1234567890",
                    company="Example Inc",
                ),
            ),
            "hubspot_2": HubSpotContact(
                id="hubspot_2",
                properties=HubSpotContactProperties(
                    firstname="Jane",
                    lastname="Smith",
                    email="jane.smith@example.com",
                    linkedin_id="linkedin_2",
                ),
            ),
        }
        self._next_id = 1000

    def get_all_contacts(self) -> list[HubSpotContact]:
        """Pull all contacts from HubSpot CRM."""
        return list(self._contacts.values())

    def create_contact(self, contact_data: dict) -> HubSpotContact:
        """Create a new contact in HubSpot."""
        hubspot_id = f"hubspot_{self._next_id}"
        self._next_id += 1

        contact = HubSpotContact(
            id=hubspot_id,
            properties=HubSpotContactProperties(
                firstname=contact_data.get("first_name"),
                lastname=contact_data.get("last_name"),
                email=contact_data.get("email"),
                linkedin_id=contact_data.get("linkedin_id"),
                phone=contact_data.get("phone"),
                company=contact_data.get("company"),
            ),
        )

        self._contacts[hubspot_id] = contact
        return contact

    def update_contact(self, contact_id: str, contact_data: dict) -> HubSpotContact:
        """Update an existing contact in HubSpot."""
        if contact_id not in self._contacts:
            raise ContactNotFoundError(contact_id)

        existing = self._contacts[contact_id]

        updated_contact = HubSpotContact(
            id=contact_id,
            properties=HubSpotContactProperties(
                firstname=contact_data.get("first_name") or existing.properties.firstname,
                lastname=contact_data.get("last_name") or existing.properties.lastname,
                email=contact_data.get("email") or existing.properties.email,
                linkedin_id=contact_data.get("linkedin_id") or existing.properties.linkedin_id,
                phone=contact_data.get("phone") or existing.properties.phone,
                company=contact_data.get("company") or existing.properties.company,
            ),
        )

        self._contacts[contact_id] = updated_contact
        return updated_contact
