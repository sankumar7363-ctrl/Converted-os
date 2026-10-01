from typing import Any

from core.models.tool_call import ToolPlan
from core.executor.tool_system import ToolSystem
from core.executor.tool_argument_validator import (
    ToolArgumentValidator,
)


class ToolPlanExecutor:

    def __init__(
        self,
        tool_system: ToolSystem,
    ):

        self.tool_system = tool_system

        self.validator = (
            ToolArgumentValidator()
        )

        self.pending_plans: dict[
            str,
            ToolPlan,
        ] = {}

        self.pending_indexes: dict[
            str,
            int,
        ] = {}

    def execute(
        self,
        task_id: str,
        plan: ToolPlan,
        start_index: int = 0,
    ) -> list[Any]:

        results = []

        print(
            f"[TOOL PLAN] Executing plan: "
            f"{plan.goal}"
        )

        for index in range(
            start_index,
            len(plan.calls),
        ):

            call = plan.calls[index]

            print(
                f"[TOOL PLAN] "
                f"Call {index + 1}: "
                f"{call.tool_name}"
            )

            # -----------------------------------------
            # Find tool definition
            # -----------------------------------------

            tool = self.tool_system.catalog.get_definition(
                call.tool_name
            )

            if tool is None:

                raise ValueError(
                    f"Tool not found in catalog: "
                    f"{call.tool_name}"
                )

            # -----------------------------------------
            # Validate arguments
            # -----------------------------------------

            self.validator.validate(
                tool,
                call.arguments,
            )

            # -----------------------------------------
            # Safe execution
            # -----------------------------------------

            result = (
                self.tool_system.safe_executor.execute(
                    task_id=task_id,
                    tool_name=call.tool_name,
                    **call.arguments,
                )
            )

            results.append(result)

            # -----------------------------------------
            # Permission pause
            # -----------------------------------------

            if (
                isinstance(result, dict)
                and result.get("status")
                == "pending"
            ):

                print(
                    "[TOOL PLAN] "
                    "Execution paused for permission"
                )

                self.pending_plans[
                    task_id
                ] = plan

                self.pending_indexes[
                    task_id
                ] = index

                return results

        # ---------------------------------------------
        # Plan completed
        # ---------------------------------------------

        self.pending_plans.pop(
            task_id,
            None,
        )

        self.pending_indexes.pop(
            task_id,
            None,
        )

        print(
            "[TOOL PLAN] "
            "Plan completed"
        )

        return results

    def approve_pending(
        self,
        task_id: str,
    ) -> list[Any] | None:

        if task_id not in self.pending_plans:

            print(
                "[TOOL PLAN] "
                f"No pending plan: {task_id}"
            )

            return None

        if task_id not in self.pending_indexes:

            print(
                "[TOOL PLAN] "
                f"No pending call: {task_id}"
            )

            return None

        plan = self.pending_plans[
            task_id
        ]

        index = self.pending_indexes[
            task_id
        ]

        call = plan.calls[index]

        print(
            f"[TOOL PLAN] Approving: "
            f"{call.tool_name}"
        )

        approved = (
            self.tool_system.permissions.approve(
                task_id
            )
        )

        if not approved:

            print(
                "[TOOL PLAN] "
                "Permission approval failed"
            )

            return None

        self.pending_plans.pop(
            task_id,
            None,
        )

        self.pending_indexes.pop(
            task_id,
            None,
        )

        # Validate again before execution.
        tool = self.tool_system.catalog.get_definition(
            call.tool_name
        )

        if tool is None:

            raise ValueError(
                f"Tool not found in catalog: "
                f"{call.tool_name}"
            )

        self.validator.validate(
            tool,
            call.arguments,
        )

        result = (
            self.tool_system.executor.execute(
                call.tool_name,
                **call.arguments,
            )
        )

        results = [
            {
                "status": "allow",
                "tool": call.tool_name,
                "result": result,
            }
        ]

        print(
            f"[TOOL PLAN] "
            f"Approved call executed: "
            f"{call.tool_name}"
        )

        remaining_results = self.execute(
            task_id=task_id,
            plan=plan,
            start_index=index + 1,
        )

        results.extend(
            remaining_results
        )

        return results

    def deny_pending(
        self,
        task_id: str,
    ) -> bool:

        if task_id not in self.pending_plans:

            print(
                "[TOOL PLAN] "
                f"No pending plan: {task_id}"
            )

            return False

        denied = (
            self.tool_system.permissions.deny(
                task_id
            )
        )

        if not denied:

            print(
                "[TOOL PLAN] "
                "Permission denial failed"
            )

            return False

        self.pending_plans.pop(
            task_id,
            None,
        )

        self.pending_indexes.pop(
            task_id,
            None,
        )

        print(
            "[TOOL PLAN] "
            "Plan stopped after permission denial"
        )

        return True
