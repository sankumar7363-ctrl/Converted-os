from core.models.tool_call import ToolPlan
from core.models.tool_result import ToolResultStatus
from core.executor.tool_system import ToolSystem
from core.executor.tool_argument_validator import ToolArgumentValidator
from core.observer.tool_observer import ToolObserver


class ObservedToolPlanExecutor:

    def __init__(
        self,
        tool_system: ToolSystem,
        observer: ToolObserver | None = None,
    ):
        self.tool_system = tool_system
        self.validator = ToolArgumentValidator()
        self.observer = observer if observer is not None else ToolObserver()

    def execute(
        self,
        task_id: str,
        plan: ToolPlan,
    ):

        observations = []

        print(f"\n[OBSERVED PLAN] Executing: {plan.goal}")

        for index, call in enumerate(plan.calls):

            print(
                f"\n[OBSERVED PLAN] Step {index + 1}: "
                f"{call.tool_name}"
            )

            try:
                tool = self.tool_system.catalog.get_definition(
                    call.tool_name
                )

                if tool is None:
                    raise ValueError(
                        f"Tool not found in catalog: {call.tool_name}"
                    )

                self.validator.validate(
                    tool,
                    call.arguments,
                )

                result = self.tool_system.safe_executor.execute(
                    task_id=task_id,
                    tool_name=call.tool_name,
                    **call.arguments,
                )

                if (
                    isinstance(result, dict)
                    and result.get("status") == "pending"
                ):
                    observation = (
                        self.observer.observe_pending_permission(
                            step_index=index,
                            tool_name=call.tool_name,
                            result=result,
                        )
                    )

                    observations.append(observation)

                    print(
                        "[OBSERVED PLAN] "
                        "Execution paused for permission"
                    )

                    break

                # Detect structured tool failure.
                if (
                    isinstance(result, dict)
                    and result.get("result") is not None
                    and isinstance(result["result"], dict)
                    and result["result"].get("success") is False
                ):
                    tool_result = result["result"]

                    error_message = (
                        tool_result.get("stderr")
                        or f"Tool returned failure with "
                           f"return code "
                           f"{tool_result.get('return_code')}"
                    )

                    if tool_result.get("timed_out"):
                        error = TimeoutError(
                            "Terminal command timed out"
                        )
                    else:
                        error = RuntimeError(
                            f"Command failed: {error_message.strip()}"
                        )

                    observation = self.observer.observe_failure(
                        step_index=index,
                        tool_name=call.tool_name,
                        error=error,
                    )

                    observations.append(observation)

                    print(
                        "[OBSERVED PLAN] "
                        "Stopping after tool-reported failure"
                    )

                    break

                observation = self.observer.observe_success(
                    step_index=index,
                    tool_name=call.tool_name,
                    result=result,
                )

                observations.append(observation)

            except Exception as error:

                observation = self.observer.observe_failure(
                    step_index=index,
                    tool_name=call.tool_name,
                    error=error,
                )

                observations.append(observation)

                print(
                    "[OBSERVED PLAN] "
                    "Stopping after failed step"
                )

                break

        successful_steps = sum(
            1
            for observation in observations
            if observation.status == ToolResultStatus.SUCCESS
        )

        failed_steps = sum(
            1
            for observation in observations
            if observation.status == ToolResultStatus.FAILURE
        )

        pending_steps = sum(
            1
            for observation in observations
            if observation.status
            == ToolResultStatus.PENDING_PERMISSION
        )

        print("\n[OBSERVED PLAN] Summary:")
        print(
            f"[OBSERVED PLAN] Successful steps: "
            f"{successful_steps}"
        )
        print(
            f"[OBSERVED PLAN] Failed steps: "
            f"{failed_steps}"
        )
        print(
            f"[OBSERVED PLAN] Pending permission: "
            f"{pending_steps}"
        )

        return observations
