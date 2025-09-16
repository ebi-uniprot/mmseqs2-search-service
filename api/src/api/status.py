"""Status messages for mmseqs2 job."""

from enum import StrEnum


class TaskStatus(StrEnum):
    """Enum containing task status values."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
