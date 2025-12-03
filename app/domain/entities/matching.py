from dataclasses import dataclass

from app.schemas import ContactResponse
from app.domain.entities.hubspot import HubSpotContact


@dataclass(frozen=True)
class MatchResult:
    """Result of contact matching operation."""

    matched: list[tuple[ContactResponse, HubSpotContact]]
    unmatched: list[ContactResponse]
