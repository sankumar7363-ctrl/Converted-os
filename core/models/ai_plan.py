from pydantic import BaseModel, Field


class AIPlanStep(BaseModel):
    description: str
    reason: str | None = None


class AIPlan(BaseModel):
    goal: str
    steps: list[AIPlanStep] = Field(default_factory=list)
