from core.ai.model import AIModel

from core.models.tool_call import (
    ToolCall,
    ToolPlan,
)

from core.models.tool_result import (
    ToolCallResult,
    ToolResultStatus,
)

from core.executor.observed_tool_plan_executor import (
    ObservedToolPlanExecutor,
)

from core.executor.tool_plan_parser import (
    ToolPlanParser,
)

from core.executor.tool_system import ToolSystem

from core.executor.tool_argument_validator import (
    ToolArgumentValidator,
)

from core.observer.tool_observer import (
    ToolObserver,
)


class RecoveryToolPlanExecutor:

    def __init__(
        self,
        tool_system: ToolSystem,
        ai_model: AIModel,
        observer: ToolObserver | None = None,
    ):

        self.tool_system = tool_system
        self.ai_model = ai_model

        self.observer = (
            observer
            if observer is not None
            else ToolObserver()
        )

        self.validator = ToolArgumentValidator()
        self.parser = ToolPlanParser()

        self.observed_executor = (
            ObservedToolPlanExecutor(
                tool_system=tool_system,
                observer=self.observer,
            )
        )

        # Original task waiting for permission.
        self.pending_tasks: dict[str, ToolPlan] = {}

        # Original plan step waiting for permission.
        self.pending_indexes: dict[str, int] = {}

        # Recovery action waiting for permission.
        self.pending_recovery_calls: dict[str, ToolCall] = {}

        # Failed step that caused the recovery.
        self.pending_recovery_indexes: dict[str, int] = {}

    # ---------------------------------------------------------
    # RECOVERY PROMPT
    # ---------------------------------------------------------

    def _build_recovery_prompt(
        self,
        plan: ToolPlan,
        failed_step: ToolCallResult,
    ) -> str:

        failed_call = plan.calls[failed_step.step_index]

        available_tools = (
            self.tool_system.catalog.describe_tools()
        )

        tool_descriptions = []

        for tool in available_tools:

            parameters = []

            for parameter in tool.parameters:

                parameters.append(
                    f"- {parameter.name}: "
                    f"{parameter.description}"
                )

            parameter_text = (
                "\n".join(parameters)
                if parameters
                else "None"
            )

            tool_descriptions.append(
                f"Tool: {tool.name}\n"
                f"Description: {tool.description}\n"
                f"Parameters:\n"
                f"{parameter_text}"
            )

        tools_text = (
            "\n\n".join(tool_descriptions)
            if tool_descriptions
            else "No tools available."
        )

        return f"""
You are the recovery planner of Converted OS.

A multi-step task was being executed.

Original goal:
{plan.goal}

The failed step was:

Step index:
{failed_step.step_index}

Tool:
{failed_call.tool_name}

Arguments:
{failed_call.arguments}

Failure:
{failed_step.error}

Available tools:

{tools_text}

Create a replacement tool call that can accomplish
the failed step.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "goal": "Recovery for failed step",
    "calls": [
        {{
            "tool_name": "tool_name",
            "arguments": {{}}
        }}
    ]
}}

Rules:

1. Use only available tools.
2. Use exact tool names.
3. Use exact parameter names.
4. Include all required parameters.
5. Return exactly one recovery call.
6. Do not include explanations.
""".strip()

    # ---------------------------------------------------------
    # CREATE RECOVERY ACTION
    # ---------------------------------------------------------

    def _create_recovery_call(
        self,
        plan: ToolPlan,
        failed_step: ToolCallResult,
    ) -> ToolCall:

        prompt = self._build_recovery_prompt(
            plan=plan,
            failed_step=failed_step,
        )

        print(
            "\n[RECOVERY PLANNER] "
            "Generating recovery action"
        )

        response = self.ai_model.generate(prompt)

        recovery_plan = self.parser.parse(response)

        if len(recovery_plan.calls) != 1:

            raise ValueError(
                "Recovery AI must return "
                "exactly one tool call"
            )

        recovery_call = recovery_plan.calls[0]

        print(
            "[RECOVERY PLANNER] "
            f"Recovery tool: "
            f"{recovery_call.tool_name}"
        )

        return recovery_call

    # ---------------------------------------------------------
    # EXECUTE RECOVERY ACTION
    # ---------------------------------------------------------

    def _execute_recovery(
        self,
        task_id: str,
        step_index: int,
        recovery_call: ToolCall,
    ) -> ToolCallResult:

        try:

            tool = (
                self.tool_system.catalog.get_definition(
                    recovery_call.tool_name
                )
            )

            if tool is None:

                raise ValueError(
                    f"Recovery tool not found: "
                    f"{recovery_call.tool_name}"
                )

            self.validator.validate(
                tool,
                recovery_call.arguments,
            )

            result = (
                self.tool_system.safe_executor.execute(
                    task_id=task_id,
                    tool_name=recovery_call.tool_name,
                    **recovery_call.arguments,
                )
            )

            if (
                isinstance(result, dict)
                and result.get("status") == "pending"
            ):

                return (
                    self.observer.observe_pending_permission(
                        step_index=step_index,
                        tool_name=recovery_call.tool_name,
                        result=result,
                    )
                )

            # Detect actual tool failure.
            if (
                isinstance(result, dict)
                and result.get("result") is not None
                and isinstance(result["result"], dict)
                and result["result"].get("success") is False
            ):

                tool_result = result["result"]

                if tool_result.get("timed_out"):

                    error = TimeoutError(
                        "Command timed out"
                    )

                else:

                    error_message = (
                        tool_result.get("stderr")
                        or (
                            "Command failed with "
                            f"return code "
                            f"{tool_result.get('return_code')}"
                        )
                    )

                    error = RuntimeError(
                        f"Command failed: "
                        f"{error_message.strip()}"
                    )

                return self.observer.observe_failure(
                    step_index=step_index,
                    tool_name=recovery_call.tool_name,
                    error=error,
                )

            return self.observer.observe_success(
                step_index=step_index,
                tool_name=recovery_call.tool_name,
                result=result,
            )

        except Exception as error:

            return self.observer.observe_failure(
                step_index=step_index,
                tool_name=recovery_call.tool_name,
                error=error,
            )

    # ---------------------------------------------------------
    # HANDLE FAILURE
    # ---------------------------------------------------------

    def _recover_from_failure(
        self,
        task_id: str,
        plan: ToolPlan,
        observations: list[ToolCallResult],
        failed_step: ToolCallResult,
    ) -> list[ToolCallResult]:

        print(
            "\n[RECOVERY EXECUTOR] "
            f"Failure detected at step "
            f"{failed_step.step_index + 1}"
        )

        recovery_call = (
            self._create_recovery_call(
                plan=plan,
                failed_step=failed_step,
            )
        )

        if recovery_call is None:
            print(
                "[RECOVERY EXECUTOR] "
                "No recovery action available"
            )

            self._clear_pending(task_id)

            return observations

        print(
            "[RECOVERY EXECUTOR] "
            f"Recovery action: {recovery_call.tool_name}"
        )

        try:

            tool = (
                self.tool_system.catalog.get_definition(
                    recovery_call.tool_name
                )
            )

            if tool is None:
                raise ValueError(
                    f"Recovery tool not found: "
                    f"{recovery_call.tool_name}"
                )

            self.validator.validate(
                tool,
                recovery_call.arguments,
            )

            result = self.tool_system.safe_executor.execute(
                task_id=task_id,
                tool_name=recovery_call.tool_name,
                **recovery_call.arguments,
            )

            if (
                isinstance(result, dict)
                and result.get("status") == "pending"
            ):
                recovery_observation = (
                    self.observer.observe_pending_permission(
                        step_index=failed_step.step_index,
                        tool_name=recovery_call.tool_name,
                        result=result,
                    )
                )

                self.pending_recovery_calls[task_id] = (
                    recovery_call
                )

                self.pending_recovery_indexes[task_id] = (
                    failed_step.step_index
                )

                print(
                    "[RECOVERY EXECUTOR] "
                    "Recovery requires permission"
                )

                return observations + [
                    recovery_observation
                ]

            if (
                isinstance(result, dict)
                and result.get("result") is not None
                and isinstance(result["result"], dict)
                and result["result"].get("success") is False
            ):

                tool_result = result["result"]

                if tool_result.get("timed_out"):
                    error = TimeoutError(
                        "Recovery command timed out"
                    )

                else:
                    error_message = (
                        tool_result.get("stderr")
                        or (
                            "Recovery command failed with "
                            f"return code "
                            f"{tool_result.get('return_code')}"
                        )
                    )

                    error = RuntimeError(
                        f"Recovery command failed: "
                        f"{error_message.strip()}"
                    )

                recovery_observation = (
                    self.observer.observe_failure(
                        step_index=failed_step.step_index,
                        tool_name=recovery_call.tool_name,
                        error=error,
                    )
                )

                return observations + [
                    recovery_observation
                ]

            recovery_observation = (
                self.observer.observe_success(
                    step_index=failed_step.step_index,
                    tool_name=recovery_call.tool_name,
                    result=result,
                )
            )

            return observations + [
                recovery_observation
            ]

        except Exception as error:

            recovery_observation = (
                self.observer.observe_failure(
                    step_index=failed_step.step_index,
                    tool_name=recovery_call.tool_name,
                    error=error,
                )
            )

            return observations + [
                recovery_observation
            ]

    # ---------------------------------------------------------
    # CONTINUE REMAINING WORKFLOW
    # ---------------------------------------------------------

    def _continue_remaining(
        self,
        task_id: str,
        plan: ToolPlan,
        observations: list[ToolCallResult],
        next_index: int,
    ) -> list[ToolCallResult]:

        remaining_plan = ToolPlan(
            goal=plan.goal,
            calls=plan.calls[next_index:],
        )

        if not remaining_plan.calls:

            print(
                "[RECOVERY EXECUTOR] "
                "No remaining steps"
            )

            self._clear_pending(task_id)

            return observations

        print(
            "\n[RECOVERY EXECUTOR] "
            "Continuing remaining steps"
        )

        remaining_results = (
            self.observed_executor.execute(
                task_id=task_id,
                plan=remaining_plan,
            )
        )

        for result in remaining_results:

            result.step_index += next_index

        observations.extend(remaining_results)

        for result in remaining_results:

            if (
                result.status
                == ToolResultStatus.PENDING_PERMISSION
            ):

                self.pending_tasks[task_id] = plan
                self.pending_indexes[task_id] = (
                    result.step_index
                )

                print(
                    "[RECOVERY EXECUTOR] "
                    "Workflow paused during continuation"
                )

                return observations

        self._clear_pending(task_id)

        return observations

    # ---------------------------------------------------------
    # CLEAR PENDING STATE
    # ---------------------------------------------------------

    def _clear_pending(
        self,
        task_id: str,
    ):

        self.pending_tasks.pop(task_id, None)
        self.pending_indexes.pop(task_id, None)
        self.pending_recovery_calls.pop(task_id, None)
        self.pending_recovery_indexes.pop(task_id, None)

    # ---------------------------------------------------------
    # FIRST EXECUTION
    # ---------------------------------------------------------

    def execute(
        self,
        task_id: str,
        plan: ToolPlan,
    ) -> list[ToolCallResult]:

        print(
            f"\n[RECOVERY EXECUTOR] "
            f"Starting task: {plan.goal}"
        )

        observations = (
            self.observed_executor.execute(
                task_id=task_id,
                plan=plan,
            )
        )

        pending_observations = [
            observation
            for observation in observations
            if observation.status
            == ToolResultStatus.PENDING_PERMISSION
        ]

        if pending_observations:

            pending = pending_observations[0]

            self.pending_tasks[task_id] = plan
            self.pending_indexes[task_id] = (
                pending.step_index
            )

            print(
                "\n[RECOVERY EXECUTOR] "
                "Execution paused for permission"
            )

            return observations

        failed_observations = [
            observation
            for observation in observations
            if observation.status
            == ToolResultStatus.FAILURE
        ]

        if not failed_observations:

            print(
                "[RECOVERY EXECUTOR] "
                "Plan completed without failure"
            )

            return observations

        failed_step = failed_observations[0]

        return self._recover_from_failure(
            task_id=task_id,
            plan=plan,
            observations=observations,
            failed_step=failed_step,
        )

    # ---------------------------------------------------------
    # RESUME
    # ---------------------------------------------------------

    def resume(
        self,
        task_id: str,
    ) -> list[ToolCallResult] | None:

        if task_id not in self.pending_tasks:

            print(
                "[RECOVERY EXECUTOR] "
                f"No paused task: {task_id}"
            )

            return None

        plan = self.pending_tasks[task_id]

        # -----------------------------------------------------
        # CASE 1: RECOVERY ACTION IS WAITING FOR PERMISSION
        # -----------------------------------------------------

        if task_id in self.pending_recovery_calls:

            recovery_call = (
                self.pending_recovery_calls[task_id]
            )

            failed_index = (
                self.pending_recovery_indexes[task_id]
            )

            if not self.tool_system.permissions.is_pending(
                task_id
            ):

                print(
                    "[RECOVERY EXECUTOR] "
                    "Recovery permission is not pending"
                )

                return None

            approved = (
                self.tool_system.permissions.approve(
                    task_id
                )
            )

            if not approved:

                print(
                    "[RECOVERY EXECUTOR] "
                    "Recovery permission approval failed"
                )

                return None

            print(
                "\n[RECOVERY EXECUTOR] "
                "Resuming recovery action"
            )

            try:

                tool = (
                    self.tool_system.catalog.get_definition(
                        recovery_call.tool_name
                    )
                )

                if tool is None:

                    raise ValueError(
                        "Recovery tool not found: "
                        f"{recovery_call.tool_name}"
                    )

                self.validator.validate(
                    tool,
                    recovery_call.arguments,
                )

                # Permission has already been approved.
                # Execute the exact approved recovery action
                # directly instead of sending it through the
                # permission layer again.
                print(
                    "[RECOVERY EXECUTOR] "
                    "Executing approved recovery action"
                )

                result = (
                    self.tool_system.executor.execute(
                        recovery_call.tool_name,
                        **recovery_call.arguments,
                    )
                )

                # Detect actual recovery-tool failure.
                if (
                    isinstance(result, dict)
                    and result.get("success") is False
                ):

                    if result.get("timed_out"):

                        error = TimeoutError(
                            "Recovery command timed out"
                        )

                    else:

                        error_message = (
                            result.get("stderr")
                            or (
                                "Recovery command failed with "
                                f"return code "
                                f"{result.get('return_code')}"
                            )
                        )

                        error = RuntimeError(
                            "Recovery command failed: "
                            f"{error_message.strip()}"
                        )

                    recovery_observation = (
                        self.observer.observe_failure(
                            step_index=failed_index,
                            tool_name=recovery_call.tool_name,
                            error=error,
                        )
                    )

                    self._clear_pending(task_id)

                    return [recovery_observation]

                recovery_observation = (
                    self.observer.observe_success(
                        step_index=failed_index,
                        tool_name=recovery_call.tool_name,
                        result=result,
                    )
                )

                print(
                    "[RECOVERY EXECUTOR] "
                    "Recovery succeeded"
                )

                # Recovery is finished. Remove ONLY recovery
                # state. The original workflow state must remain.
                self.pending_recovery_calls.pop(
                    task_id,
                    None,
                )

                self.pending_recovery_indexes.pop(
                    task_id,
                    None,
                )

                return self._continue_remaining(
                    task_id=task_id,
                    plan=plan,
                    observations=[
                        recovery_observation
                    ],
                    next_index=failed_index + 1,
                )

            except Exception as error:

                recovery_observation = (
                    self.observer.observe_failure(
                        step_index=failed_index,
                        tool_name=recovery_call.tool_name,
                        error=error,
                    )
                )

                self._clear_pending(task_id)

                return [recovery_observation]

        # -----------------------------------------------------
        # CASE 2: ORIGINAL STEP IS WAITING FOR PERMISSION
        # -----------------------------------------------------

        if task_id not in self.pending_indexes:

            print(
                "[RECOVERY EXECUTOR] "
                "No paused step: "
                f"{task_id}"
            )

            return None

        step_index = self.pending_indexes[task_id]

        if not self.tool_system.permissions.is_pending(
            task_id
        ):

            print(
                "[RECOVERY EXECUTOR] "
                "Task is not waiting for permission"
            )

            return None

        approved = (
            self.tool_system.permissions.approve(
                task_id
            )
        )

        if not approved:

            print(
                "[RECOVERY EXECUTOR] "
                "Permission approval failed"
            )

            return None

        print(
            "\n[RECOVERY EXECUTOR] "
            f"Resuming step {step_index + 1}"
        )

        call = plan.calls[step_index]

        try:

            tool = (
                self.tool_system.catalog.get_definition(
                    call.tool_name
                )
            )

            if tool is None:

                raise ValueError(
                    f"Tool not found: {call.tool_name}"
                )

            self.validator.validate(
                tool,
                call.arguments,
            )

            result = self.tool_system.executor.execute(
                call.tool_name,
                **call.arguments,
            )

            if (
                isinstance(result, dict)
                and result.get("success") is False
            ):

                if result.get("timed_out"):

                    error = TimeoutError(
                        "Command timed out"
                    )

                else:

                    error_message = (
                        result.get("stderr")
                        or (
                            "Command failed with "
                            f"return code "
                            f"{result.get('return_code')}"
                        )
                    )

                    error = RuntimeError(
                        f"Command failed: "
                        f"{error_message.strip()}"
                    )

                observation = (
                    self.observer.observe_failure(
                        step_index=step_index,
                        tool_name=call.tool_name,
                        error=error,
                    )
                )

                return self._recover_from_failure(
                    task_id=task_id,
                    plan=plan,
                    observations=[observation],
                    failed_step=observation,
                )

            observation = (
                self.observer.observe_success(
                    step_index=step_index,
                    tool_name=call.tool_name,
                    result=result,
                )
            )

        except Exception as error:

            observation = (
                self.observer.observe_failure(
                    step_index=step_index,
                    tool_name=call.tool_name,
                    error=error,
                )
            )

        if not observation.success:

            return self._recover_from_failure(
                task_id=task_id,
                plan=plan,
                observations=[observation],
                failed_step=observation,
            )

        return self._continue_remaining(
            task_id=task_id,
            plan=plan,
            observations=[observation],
            next_index=step_index + 1,
        )
