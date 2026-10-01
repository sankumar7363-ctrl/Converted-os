from enum import Enum
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class OutcomeStatus(str, Enum):

    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    WAITING = "waiting"


class TaskOutcome(BaseModel):

    id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    task_id: str

    success: bool

    status: OutcomeStatus

    summary: str

    created_at: datetime = Field(
        default_factory=datetime.now
    )
