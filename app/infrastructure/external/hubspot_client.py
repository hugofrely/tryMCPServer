"""
Mocked HubSpot API client.
In a real scenario, this would make actual HTTP requests to HubSpot API.
"""


class HubSpotClient:
    def __init__(self):
        self._contacts = {
            "hubspot_1": {
                "id": "hubspot_1",
                "properties": {
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": "john.doe@example.com",
                    "linkedin_id": "linkedin_1",
                    "phone": "1234567890",
                    "company": "Example Inc",
                },
            },
            "hubspot_2": {
                "id": "hubspot_2",
                "properties": {
                    "firstname": "Jane",
                    "lastname": "Smith",
                    "email": "jane.smith@example.com",
                    "linkedin_id": "linkedin_2",
                },
            },
        }
        self._next_id = 1000

    def get_all_contacts(self):
        """Pull all contacts from HubSpot CRM"""
        return list(self._contacts.values())

    def create_contact(self, contact_data):
        """Create a new contact in HubSpot"""
        hubspot_id = f"hubspot_{self._next_id}"
        self._next_id += 1

        contact = {
            "id": hubspot_id,
            "properties": {
                "firstname": contact_data.get("first_name", ""),
                "lastname": contact_data.get("last_name", ""),
                "email": contact_data.get("email", ""),
                "linkedin_id": contact_data.get("linkedin_id", ""),
                "phone": contact_data.get("phone", ""),
                "company": contact_data.get("company", ""),
            },
        }

        self._contacts[hubspot_id] = contact
        return contact

    def update_contact(self, hubspot_id, contact_data):
        """Update an existing contact in HubSpot"""
        if hubspot_id not in self._contacts:
            raise ValueError(f"Contact {hubspot_id} not found")

        contact = self._contacts[hubspot_id]
        contact["properties"].update(
            {
                "firstname": contact_data.get(
                    "first_name", contact["properties"].get("firstname", "")
                ),
                "lastname": contact_data.get(
                    "last_name", contact["properties"].get("lastname", "")
                ),
                "email": contact_data.get(
                    "email", contact["properties"].get("email", "")
                ),
                "linkedin_id": contact_data.get(
                    "linkedin_id", contact["properties"].get("linkedin_id", "")
                ),
                "phone": contact_data.get(
                    "phone", contact["properties"].get("phone", "")
                ),
                "company": contact_data.get(
                    "company", contact["properties"].get("company", "")
                ),
            }
        )

        return contact
