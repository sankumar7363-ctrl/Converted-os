from core.ai.model import AIModel
from core.executor.recovery_tool_plan_executor import RecoveryToolPlanExecutor
from core.executor.tool_system import ToolSystem
from core.executor.tool_definition import ToolDefinition, ToolParameter, ToolRisk
from core.executor.tools.terminal_tools import TerminalTools
from core.models.tool_call import ToolCall
from core.models.tool_call import ToolPlan


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


def main():
    tool_system = ToolSystem()

    terminal_tools = TerminalTools()

    terminal_definition = ToolDefinition(
        name="run_command",
        description="Run a terminal command inside the workspace",
        risk=ToolRisk.LOW,
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
        terminal_definition,
        terminal_tools.run_command,
    )

    ai_model = FakeTerminalRecoveryAI()

    executor = RecoveryToolPlanExecutor(
        tool_system=tool_system,
        ai_model=ai_model,
    )

    plan = ToolPlan(
        goal="Recover and continue a multi-step terminal workflow",
        calls=[
            ToolCall(
                tool_name="run_command",
                arguments={
                    "command": "bash -c 'echo intentional-error >&2; exit 1'",
                    "timeout": 10,
                },
            ),
            ToolCall(
                tool_name="run_command",
                arguments={
                    "command": "echo Original step 2 executed",
                    "timeout": 10,
                },
            ),
            ToolCall(
                tool_name="run_command",
                arguments={
                    "command": "echo Original step 3 executed",
                    "timeout": 10,
                },
            ),
        ],
    )

    task_id = "terminal-recovery-continuation-test"

    observations = executor.execute(
        task_id=task_id,
        plan=plan,
    )

    print("\n[TEST] Final observations:")

    for observation in observations:
        print(observation)

    # We expect:
    # 1. Original Step 1 fails.
    # 2. AI recovery succeeds.
    # 3. Original Step 2 executes successfully.
    # 4. Original Step 3 executes successfully.

    assert len(observations) == 4

    # Original failed step.
    first = observations[0]

    assert first.tool_name == "run_command"
    assert first.success is False
    assert first.status.value == "failure"
    assert "intentional-error" in first.error

    # Recovery action.
    recovery = observations[1]

    assert recovery.tool_name == "run_command"
    assert recovery.success is True
    assert recovery.status.value == "success"
    assert recovery.result["result"]["success"] is True
    assert "Recovery successful" in recovery.result["result"]["stdout"]

    # Original Step 2 continued after recovery.
    second = observations[2]

    assert second.tool_name == "run_command"
    assert second.success is True
    assert second.status.value == "success"
    assert second.result["result"]["success"] is True
    assert "Original step 2 executed" in second.result["result"]["stdout"]

    # Original Step 3 continued after recovery.
    third = observations[3]

    assert third.tool_name == "run_command"
    assert third.success is True
    assert third.status.value == "success"
    assert third.result["result"]["success"] is True
    assert "Original step 3 executed" in third.result["result"]["stdout"]

    print("\n=== TERMINAL RECOVERY CONTINUATION TEST PASSED ===")
    print("=== ALL TERMINAL RECOVERY CONTINUATION TESTS PASSED ===")


if __name__ == "__main__":
    main()
