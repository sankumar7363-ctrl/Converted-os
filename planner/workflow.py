from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4


class WorkflowStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    completed: bool = False


class TemporaryWorkflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    status: WorkflowStatus = WorkflowStatus.CREATED
    steps: list[WorkflowStep] = Field(default_factory=list)

    # Indicates whether previous experience influenced this workflow
    experience_used: bool = False
