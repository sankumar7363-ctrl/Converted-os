from typing import Any

from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_definition import (
    ToolDefinition,
    ToolRisk,
)
from core.executor.tool_executor import ToolExecutor
from core.executor.tool_policy import ToolPolicy

from core.policy.permission import (
    PermissionDecision,
    PermissionManager,
)
from core.policy.policy import (
    Action,
    PolicyDecision,
    RiskLevel,
)


class SafeToolExecutor:

    def __init__(
        self,
        catalog: ToolCatalog,
        executor: ToolExecutor,
        policy: ToolPolicy | None = None,
        permissions: PermissionManager | None = None,
    ):

        self.catalog = catalog
        self.executor = executor

        self.policy = (
            policy
            if policy is not None
            else ToolPolicy()
        )

        self.permissions = (
            permissions
            if permissions is not None
            else PermissionManager()
        )

    def _create_action(
        self,
        tool: ToolDefinition,
    ) -> Action:

        risk_map = {
            ToolRisk.LOW: RiskLevel.LOW,
            ToolRisk.MEDIUM: RiskLevel.MEDIUM,
            ToolRisk.HIGH: RiskLevel.HIGH,
        }

        return Action(
            name=tool.name,
            description=tool.description,
            risk=risk_map[tool.risk],
        )

    def execute(
        self,
        task_id: str,
        tool_name: str,
        **kwargs: Any,
    ) -> Any:

        tool = self.catalog.get_definition(
            tool_name
        )

        if tool is None:

            raise ValueError(
                f"Tool not found in catalog: "
                f"{tool_name}"
            )

        print(
            f"[SAFE EXECUTOR] Checking: "
            f"{tool_name}"
        )

        policy_result = self.policy.evaluate(
            tool
        )

        # High-risk action
        if (
            policy_result.decision
            == PolicyDecision.BLOCK
        ):

            print(
                "[SAFE EXECUTOR] "
                f"Blocked: {tool_name}"
            )

            raise PermissionError(
                f"Tool blocked by policy: "
                f"{tool_name}"
            )

        # Medium-risk action
        if (
            policy_result.decision
            == PolicyDecision.ASK
        ):

            action = self._create_action(
                tool
            )

            permission = (
                self.permissions.request(
                    task_id=task_id,
                    action=action,
                )
            )

            print(
                "[SAFE EXECUTOR] Permission: "
                f"{permission.value}"
            )

            return {
                "status": permission.value,
                "tool": tool_name,
                "message": (
                    "User permission required"
                ),
            }

        # Low-risk action
        result = self.executor.execute(
            tool_name,
            **kwargs,
        )

        return {
            "status": PermissionDecision.ALLOW.value,
            "tool": tool_name,
            "result": result,
        }
