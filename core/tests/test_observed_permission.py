from core.executor.tools.terminal_tools import TerminalTools
from core.executor.tool_system import ToolSystem
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)
from core.executor.observed_tool_plan_executor import ObservedToolPlanExecutor
from core.models.tool_call import ToolCall, ToolPlan
from core.models.tool_result import ToolResultStatus


def test_observed_terminal_permission():
    tool_system = ToolSystem()

    terminal = TerminalTools()

    definition = ToolDefinition(
        name="run_command",
        description="Run a terminal command",
        risk=ToolRisk.MEDIUM,
        autonomous=False,
        parameters=[
            ToolParameter(
                name="command",
                description="Terminal command to execute",
                required=True,
            ),
            ToolParameter(
                name="timeout",
                description="Maximum execution time in seconds",
                required=False,
            ),
        ],
    )

    tool_system.register(
        definition,
        terminal.run_command,
    )

    plan = ToolPlan(
        goal="Run a terminal command",
        calls=[
            ToolCall(
                tool_name="run_command",
                arguments={
                    "command": "echo SHOULD_NOT_RUN_YET",
                    "timeout": 10,
                },
            )
        ],
    )

    executor = ObservedToolPlanExecutor(tool_system)

    observations = executor.execute(
        task_id="observed-permission-test",
        plan=plan,
    )

    assert len(observations) == 1

    observation = observations[0]

    assert observation.status == ToolResultStatus.PENDING_PERMISSION
    assert observation.success is False

    assert observation.result["status"] == "pending"

    assert tool_system.permissions.is_pending(
        "observed-permission-test"
    )

    print("\n=== OBSERVED PERMISSION TEST PASSED ===")
    print(observation)


if __name__ == "__main__":
    test_observed_terminal_permission()

    print("\n=== ALL OBSERVED PERMISSION TESTS PASSED ===")
