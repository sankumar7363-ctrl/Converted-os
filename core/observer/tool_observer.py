from core.models.tool_result import ToolCallResult, ToolResultStatus


class ToolObserver:

    def observe_success(
        self,
        step_index: int,
        tool_name: str,
        result,
    ) -> ToolCallResult:

        observation = ToolCallResult(
            step_index=step_index,
            tool_name=tool_name,
            status=ToolResultStatus.SUCCESS,
            success=True,
            result=result,
        )

        print(
            f"[TOOL OBSERVER] Step {step_index + 1}: "
            f"{tool_name} → SUCCESS"
        )

        return observation

    def observe_failure(
        self,
        step_index: int,
        tool_name: str,
        error: Exception,
    ) -> ToolCallResult:

        observation = ToolCallResult(
            step_index=step_index,
            tool_name=tool_name,
            status=ToolResultStatus.FAILURE,
            success=False,
            error=str(error),
        )

        print(
            f"[TOOL OBSERVER] Step {step_index + 1}: "
            f"{tool_name} → FAILED"
        )
        print(f"[TOOL OBSERVER] Error: {error}")

        return observation

    def observe_pending_permission(
        self,
        step_index: int,
        tool_name: str,
        result,
    ) -> ToolCallResult:

        observation = ToolCallResult(
            step_index=step_index,
            tool_name=tool_name,
            status=ToolResultStatus.PENDING_PERMISSION,
            success=False,
            result=result,
        )

        print(
            f"[TOOL OBSERVER] Step {step_index + 1}: "
            f"{tool_name} → PENDING PERMISSION"
        )

        return observation
