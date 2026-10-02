from typing import Any

from core.ai.model import AIModel

from core.agent.tool_planning_agent import (
    ToolPlanningAgent,
)

from core.executor.recovery_tool_plan_executor import (
    RecoveryToolPlanExecutor,
)

from core.executor.tool_discovery import (
    ToolDiscovery,
)

from core.executor.tool_system import (
    ToolSystem,
)

from core.observer.tool_observer import (
    ToolObserver,
)


class AutonomousToolAgent:

    def __init__(
        self,
        ai_model: AIModel,
        discovery: ToolDiscovery,
        tool_system: ToolSystem,
        observer: ToolObserver | None = None,
    ):

        self.planner = ToolPlanningAgent(
            ai_model=ai_model,
            discovery=discovery,
        )

        self.observer = (
            observer
            if observer is not None
            else ToolObserver()
        )

        self.executor = RecoveryToolPlanExecutor(
            tool_system=tool_system,
            ai_model=ai_model,
            observer=self.observer,
        )

    def run(
        self,
        task_id: str,
        goal: str,
        memories: list | None = None,
    ) -> list[Any]:

        print(
            f"\n[AUTONOMOUS AGENT] Goal: {goal}"
        )

        if memories:
            print(
                f"[AUTONOMOUS AGENT] "
                f"Using {len(memories)} relevant "
                f"experience(s)"
            )
        else:
            print(
                "[AUTONOMOUS AGENT] "
                "No previous experiences provided"
            )

        plan = self.planner.create_plan(
            goal=goal,
            memories=memories,
        )

        print(
            f"[AUTONOMOUS AGENT] "
            f"Plan created with "
            f"{len(plan.calls)} tool call(s)"
        )

        results = self.executor.execute(
            task_id=task_id,
            plan=plan,
        )

        print(
            f"[AUTONOMOUS AGENT] "
            f"Execution returned "
            f"{len(results)} result(s)"
        )

        return results
