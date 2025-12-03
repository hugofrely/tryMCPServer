from dataclasses import dataclass


@dataclass(frozen=True)
class HubSpotContactProperties:
    """Properties of a HubSpot contact."""

    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    linkedin_id: str | None = None
    phone: str | None = None
    company: str | None = None


@dataclass(frozen=True)
class HubSpotContact:
    """Domain entity representing a HubSpot contact."""

    id: str
    properties: HubSpotContactProperties

    @classmethod
    def from_dict(cls, data: dict) -> "HubSpotContact":
        """Create a HubSpotContact from a dictionary."""
        props = data.get("properties", {})
        return cls(
            id=data["id"],
            properties=HubSpotContactProperties(
                firstname=props.get("firstname"),
                lastname=props.get("lastname"),
                email=props.get("email"),
                linkedin_id=props.get("linkedin_id"),
                phone=props.get("phone"),
                company=props.get("company"),
            ),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "properties": {
                "firstname": self.properties.firstname,
                "lastname": self.properties.lastname,
                "email": self.properties.email,
                "linkedin_id": self.properties.linkedin_id,
                "phone": self.properties.phone,
                "company": self.properties.company,
            },
        }
