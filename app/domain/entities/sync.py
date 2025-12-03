from dataclasses import dataclass


@dataclass(frozen=True)
class SyncResult:
    """Result of a HubSpot sync operation."""

    created_count: int
    updated_count: int
