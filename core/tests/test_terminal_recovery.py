from core.ai.model import AIModel
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)
from core.executor.tool_system import ToolSystem
from core.executor.tools.terminal_tools import TerminalTools
from core.executor.recovery_tool_plan_executor import RecoveryToolPlanExecutor
from core.models.tool_call import ToolCall, ToolPlan
from core.models.tool_result import ToolResultStatus


class FakeTerminalRecoveryAI(AIModel):

    def generate(self, prompt: str) -> str:
        print("\n[FAKE AI] Recovery request received")

        return """
{
    "goal": "Recover the failed terminal command",
    "calls": [
        {
            "tool_name": "run_command",
            "arguments": {
                "command": "echo Recovery successful",
                "timeout": 10
            }
        }
    ]
}
"""


def build_tool_system():
    tool_system = ToolSystem()

    terminal = TerminalTools()

    definition = ToolDefinition(
        name="run_command",
        description="Run a terminal command",
        risk=ToolRisk.LOW,
        autonomous=True,
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

    return tool_system


def test_terminal_recovery():
    tool_system = build_tool_system()

    ai = FakeTerminalRecoveryAI()

    executor = RecoveryToolPlanExecutor(
        tool_system=tool_system,
        ai_model=ai,
    )

    plan = ToolPlan(
        goal="Run a terminal command successfully",
        calls=[
            ToolCall(
                tool_name="run_command",
                arguments={
                    "command": (
                        "bash -c "
                        "'echo intentional-error >&2; exit 1'"
                    ),
                    "timeout": 10,
                },
            )
        ],
    )

    observations = executor.execute(
        task_id="terminal-recovery-test",
        plan=plan,
    )

    print("\n[TEST] Final observations:")

    for observation in observations:
        print(observation)

    assert len(observations) >= 2

    first = observations[0]

    assert first.status == ToolResultStatus.FAILURE
    assert first.tool_name == "run_command"

    recovery = observations[1]

    assert recovery.status == ToolResultStatus.SUCCESS
    assert recovery.tool_name == "run_command"

    assert recovery.result["result"]["success"] is True
    assert "Recovery successful" in recovery.result["result"]["stdout"]

    print("\n=== TERMINAL RECOVERY TEST PASSED ===")


if __name__ == "__main__":
    test_terminal_recovery()

    print("\n=== ALL TERMINAL RECOVERY TESTS PASSED ===")
