from enum import Enum


class JobStatus(str, Enum):
    """Valid job statuses."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
