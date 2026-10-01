from enum import Enum

from pydantic import BaseModel


class RiskLevel(str, Enum):

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PolicyDecision(str, Enum):

    ALLOW = "allow"
    ASK = "ask"
    BLOCK = "block"


class Action(BaseModel):

    name: str
    description: str
    risk: RiskLevel


class PolicyResult(BaseModel):

    decision: PolicyDecision
    reason: str


class PolicyEngine:

    def evaluate(self, action: Action) -> PolicyResult:

        if action.risk == RiskLevel.LOW:

            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                reason="Low-risk action is allowed automatically",
            )

        if action.risk == RiskLevel.MEDIUM:

            return PolicyResult(
                decision=PolicyDecision.ASK,
                reason="Medium-risk action requires user confirmation",
            )

        return PolicyResult(
            decision=PolicyDecision.BLOCK,
            reason="High-risk action is blocked by default",
        )
