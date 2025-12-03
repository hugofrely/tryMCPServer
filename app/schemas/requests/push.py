from pydantic import BaseModel, EmailStr, Field, field_validator


class ProfileInput(BaseModel):
    """Input DTO for a single profile in push request."""

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Contact's first name",
        examples=["John"],
    )
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Contact's last name",
        examples=["Doe"],
    )
    email: EmailStr | None = Field(
        default=None,
        description="Contact's email address",
        examples=["john.doe@example.com"],
    )
    linkedin_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Contact's LinkedIn ID",
        examples=["john-doe-123"],
    )
    phone: str | None = Field(
        default=None,
        max_length=20,
        description="Contact's phone number",
        examples=["+33612345678"],
    )
    company: str | None = Field(
        default=None,
        max_length=200,
        description="Contact's company name",
        examples=["Acme Inc"],
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Validate phone number format."""
        if v is None:
            return v
        cleaned = v.replace(" ", "").replace("-", "")
        if not cleaned.replace("+", "").isdigit():
            raise ValueError(
                "Phone number must contain only digits, spaces, dashes, and optional + prefix"
            )
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v: str | None) -> str | None:
        """Strip whitespace from names."""
        if v is None:
            return v
        return v.strip()


class PushProfilesRequest(BaseModel):
    """Request DTO for pushing profiles to HubSpot."""

    profiles: list[ProfileInput] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of profiles to push to HubSpot",
    )

    @field_validator("profiles")
    @classmethod
    def validate_profiles_not_empty(cls, v: list[ProfileInput]) -> list[ProfileInput]:
        """Ensure at least one profile has identifying information."""
        for profile in v:
            if not any([profile.email, profile.linkedin_id, profile.first_name]):
                raise ValueError(
                    "Each profile must have at least one of: email, linkedin_id, or first_name"
                )
        return v
