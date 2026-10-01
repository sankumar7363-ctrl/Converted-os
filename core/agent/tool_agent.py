from typing import Any

from core.ai.model import AIModel

from core.executor.tool_discovery import (
    ToolDiscovery,
)

from core.executor.tool_plan_executor import (
    ToolPlanExecutor,
)

from core.agent.tool_planning_agent import (
    ToolPlanningAgent,
)

from core.models.tool_call import (
    ToolPlan,
)


class ToolAgent:

    def __init__(
        self,
        ai_model: AIModel,
        discovery: ToolDiscovery,
        executor: ToolPlanExecutor,
    ):

        self.planner = ToolPlanningAgent(
            ai_model=ai_model,
            discovery=discovery,
        )

        self.executor = executor

    def run(
        self,
        task_id: str,
        goal: str,
    ) -> list[Any]:

        print(
            f"\n[TOOL AGENT] Goal: {goal}"
        )

        plan = self.planner.create_plan(
            goal
        )

        print(
            "[TOOL AGENT] Tool plan generated"
        )

        print(
            f"[TOOL AGENT] "
            f"Tool calls: {len(plan.calls)}"
        )

        results = self.executor.execute(
            task_id=task_id,
            plan=plan,
        )

        print(
            "[TOOL AGENT] Tool plan execution finished"
        )

        return results

    def approve_pending(
        self,
        task_id: str,
    ) -> list[Any] | None:

        print(
            f"[TOOL AGENT] "
            f"Approving pending task: {task_id}"
        )

        return self.executor.approve_pending(
            task_id
        )

    def deny_pending(
        self,
        task_id: str,
    ) -> bool:

        print(
            f"[TOOL AGENT] "
            f"Denying pending task: {task_id}"
        )

        return self.executor.deny_pending(
            task_id
        )
