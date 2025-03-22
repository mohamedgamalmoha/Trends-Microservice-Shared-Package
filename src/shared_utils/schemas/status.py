import enum


class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RETRY = "retry"
    COMPLETED = "completed"
    FAILED = "failed"
