from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4


class TaskStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    goal: str
    status: TaskStatus = TaskStatus.CREATED
    result: str | None = None
