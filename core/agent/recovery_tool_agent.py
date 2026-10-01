from pathlib import Path
from typing import Any

from core.ai.model import AIModel

from core.agent.tool_planning_agent import (
    ToolPlanningAgent,
)

from core.executor.tool_discovery import (
    ToolDiscovery,
)

from core.executor.tool_plan_executor import (
    ToolPlanExecutor,
)

from core.observer.file_observer import (
    FileObserver,
)


class RecoveryToolAgent:

    def __init__(
        self,
        ai_model: AIModel,
        discovery: ToolDiscovery,
        executor: ToolPlanExecutor,
        observer: FileObserver,
    ):

        self.planner = ToolPlanningAgent(
            ai_model=ai_model,
            discovery=discovery,
        )

        self.executor = executor
        self.observer = observer

    def run(
        self,
        task_id: str,
        goal: str,
        expected_file: str,
        expected_content: str,
        max_attempts: int = 2,
    ) -> dict[str, Any]:

        print(
            f"\n[RECOVERY AGENT] Goal: {goal}"
        )

        for attempt in range(
            1,
            max_attempts + 1,
        ):

            print(
                f"\n[RECOVERY AGENT] "
                f"Attempt {attempt}/{max_attempts}"
            )

            if attempt == 1:

                planning_goal = goal

            else:

                planning_goal = (
                    f"Recover from the previous failed attempt. "
                    f"Original goal: {goal}. "
                    f"The expected file is {expected_file} "
                    f"and its expected content is: "
                    f"{expected_content}"
                )

            plan = self.planner.create_plan(
                planning_goal
            )

            results = self.executor.execute(
                task_id=task_id,
                plan=plan,
            )

            verified = (
                self.observer.verify_file(
                    filepath=expected_file,
                    expected_content=expected_content,
                )
            )

            if verified:

                print(
                    "[RECOVERY AGENT] "
                    "Action verified successfully"
                )

                return {
                    "success": True,
                    "verified": True,
                    "attempts": attempt,
                    "results": results,
                }

            print(
                "[RECOVERY AGENT] "
                "Verification failed"
            )

            if attempt < max_attempts:

                print(
                    "[RECOVERY AGENT] "
                    "Creating recovery plan"
                )

        print(
            "[RECOVERY AGENT] "
            "Recovery attempts exhausted"
        )

        return {
            "success": False,
            "verified": False,
            "attempts": max_attempts,
            "results": results,
        }
