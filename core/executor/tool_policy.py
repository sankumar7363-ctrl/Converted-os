from core.executor.tool_definition import (
    ToolDefinition,
    ToolRisk,
)

from core.policy.policy import (
    Action,
    PolicyDecision,
    PolicyEngine,
    PolicyResult,
    RiskLevel,
)


class ToolPolicy:

    def __init__(
        self,
        policy: PolicyEngine | None = None,
    ):

        self.policy = (
            policy
            if policy is not None
            else PolicyEngine()
        )

    def evaluate(
        self,
        tool: ToolDefinition,
    ) -> PolicyResult:

        risk_map = {
            ToolRisk.LOW: RiskLevel.LOW,
            ToolRisk.MEDIUM: RiskLevel.MEDIUM,
            ToolRisk.HIGH: RiskLevel.HIGH,
        }

        action = Action(
            name=tool.name,
            description=tool.description,
            risk=risk_map[tool.risk],
        )

        result = self.policy.evaluate(
            action
        )

        print(
            f"[TOOL POLICY] {tool.name} → "
            f"risk={tool.risk.value} → "
            f"decision={result.decision.value}"
        )

        return result
