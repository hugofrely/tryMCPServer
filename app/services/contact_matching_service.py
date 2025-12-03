from dataclasses import dataclass

from app.schemas import ContactResponse


@dataclass
class MatchResult:
    """Result of contact matching operation."""

    matched: list[tuple[ContactResponse, dict]]
    unmatched: list[ContactResponse]


class ContactMatchingService:
    """
    Service responsible for matching local contacts with HubSpot contacts.

    Matching priority:
    1. LinkedIn ID
    2. Email
    3. First name + Last name
    """

    def match_contacts(
        self,
        local_contacts: list[ContactResponse],
        hubspot_contacts: list[dict],
    ) -> MatchResult:
        """
        Match local contacts with HubSpot contacts.

        Returns a MatchResult containing matched pairs and unmatched contacts.
        """
        matched: list[tuple[ContactResponse, dict]] = []
        unmatched: list[ContactResponse] = []

        for local_contact in local_contacts:
            hubspot_match = self._find_match(local_contact, hubspot_contacts)

            if hubspot_match:
                matched.append((local_contact, hubspot_match))
            else:
                unmatched.append(local_contact)

        return MatchResult(matched=matched, unmatched=unmatched)

    def _find_match(
        self,
        local_contact: ContactResponse,
        hubspot_contacts: list[dict],
    ) -> dict | None:
        """Find a matching HubSpot contact for a local contact."""
        for hubspot_contact in hubspot_contacts:
            if self._matches_by_linkedin_id(local_contact, hubspot_contact):
                return hubspot_contact

            if self._matches_by_email(local_contact, hubspot_contact):
                return hubspot_contact

            if self._matches_by_name(local_contact, hubspot_contact):
                return hubspot_contact

        return None

    def _matches_by_linkedin_id(
        self,
        local_contact: ContactResponse,
        hubspot_contact: dict,
    ) -> bool:
        """Check if contacts match by LinkedIn ID."""
        if not local_contact.linkedin_id:
            return False

        hubspot_linkedin_id = hubspot_contact["properties"].get("linkedin_id")
        return hubspot_linkedin_id == local_contact.linkedin_id

    def _matches_by_email(
        self,
        local_contact: ContactResponse,
        hubspot_contact: dict,
    ) -> bool:
        """Check if contacts match by email."""
        if not local_contact.email:
            return False

        hubspot_email = hubspot_contact["properties"].get("email")
        return hubspot_email == local_contact.email

    def _matches_by_name(
        self,
        local_contact: ContactResponse,
        hubspot_contact: dict,
    ) -> bool:
        """Check if contacts match by first name + last name."""
        if not local_contact.first_name or not local_contact.last_name:
            return False

        hubspot_first = hubspot_contact["properties"].get("firstname", "").lower()
        hubspot_last = hubspot_contact["properties"].get("lastname", "").lower()

        return (
            hubspot_first == local_contact.first_name.lower()
            and hubspot_last == local_contact.last_name.lower()
        )
