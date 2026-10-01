from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4


class OutcomeStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


class ExperienceStep(BaseModel):
    step_index: int
    description: str
    tool_name: str | None = None
    success: bool
    error: str | None = None


class LearningSignal(BaseModel):
    useful: bool
    reason: str
    improvement: str | None = None


class Experience(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    goal: str

    steps: list[ExperienceStep] = Field(default_factory=list)

    outcome: OutcomeStatus
    summary: str

    recovery_used: bool = False
    learning_signal: LearningSignal | None = None
