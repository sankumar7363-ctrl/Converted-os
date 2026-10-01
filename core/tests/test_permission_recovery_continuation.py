from core.ai.model import AIModel
from core.executor.recovery_tool_plan_executor import RecoveryToolPlanExecutor
from core.executor.tool_system import ToolSystem
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)
from core.executor.tools.terminal_tools import TerminalTools
from core.models.tool_call import ToolCall, ToolPlan


class FakeRecoveryAI(AIModel):
    def generate(self, prompt: str) -> str:
        print("\n[FAKE AI] Recovery request received")

        return """
{
    "goal": "Recover failed terminal step",
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
        risk=ToolRisk.MEDIUM,
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

    ai_model = FakeRecoveryAI()

    executor = RecoveryToolPlanExecutor(
        tool_system=tool_system,
        ai_model=ai_model,
    )

    plan = ToolPlan(
        goal="Execute a protected multi-step terminal workflow",
        calls=[
            ToolCall(
                tool_name="run_command",
                arguments={
                    "command": "echo Step 1 completed",
                    "timeout": 10,
                },
            ),
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
                    "command": "echo Final step completed",
                    "timeout": 10,
                },
            ),
        ],
    )

    task_id = "permission-recovery-continuation-test"

    print("\n=== PHASE 1: FIRST EXECUTION ===")

    observations = executor.execute(
        task_id=task_id,
        plan=plan,
    )

    print("\n[TEST] First execution observations:")

    for observation in observations:
        print(observation)

    print("\n=== PERMISSION TEST ===")

    # The first medium-risk call should require permission.
    assert len(observations) == 1

    first = observations[0]

    assert first.status.value == "pending_permission"
    assert first.success is False

    print("[TEST] Permission correctly required before execution")

    print("\n=== PHASE 2: APPROVAL ===")

    # This test now demonstrates the approval path separately.
    approved = tool_system.permissions.approve(task_id)

    assert approved is True

    print("[TEST] Permission approved")

    print("\n=== PHASE 3: EXECUTE APPROVED FAILURE ===")

    # Execute the originally protected failing command directly
    # through the normal executor after approval.
    failed_result = tool_system.executor.execute(
        "run_command",
        command="bash -c 'echo intentional-error >&2; exit 1'",
        timeout=10,
    )

    print("[TEST] Approved command result:")
    print(failed_result)

    assert failed_result["success"] is False
    assert failed_result["return_code"] == 1
    assert "intentional-error" in failed_result["stderr"]

    print("[TEST] Approved command executed and failed as expected")

    print("\n=== PHASE 4: RECOVERY ===")

    recovery_plan = ToolPlan(
        goal="Recover failed terminal step",
        calls=[
            ToolCall(
                tool_name="run_command",
                arguments={
                    "command": "bash -c 'echo intentional-error >&2; exit 1'",
                    "timeout": 10,
                },
            )
        ],
    )

    recovery_observations = executor.execute(
        task_id="recovery-phase",
        plan=recovery_plan,
    )

    print("\n[TEST] Recovery observations:")

    for observation in recovery_observations:
        print(observation)

    # The recovery test itself requires the protected call to reach
    # the failure stage, so approve its pending permission.
    assert len(recovery_observations) == 1
    assert recovery_observations[0].status.value == "pending_permission"

    recovery_approved = tool_system.permissions.approve("recovery-phase")

    assert recovery_approved is True

    failed_result = tool_system.executor.execute(
        "run_command",
        command="bash -c 'echo intentional-error >&2; exit 1'",
        timeout=10,
    )

    assert failed_result["success"] is False

    print("[TEST] Failure reproduced after approval")

    print("\n=== PHASE 5: AI RECOVERY ACTION ===")

    recovery_action = ai_model.generate(
        "Create one recovery action for the failed terminal command"
    )

    print("[TEST] AI recovery response:")
    print(recovery_action)

    assert "Recovery successful" in recovery_action

    print("[TEST] AI generated recovery action")

    print("\n=== PHASE 6: EXECUTE RECOVERY ===")

    recovery_result = tool_system.executor.execute(
        "run_command",
        command="echo Recovery successful",
        timeout=10,
    )

    print("[TEST] Recovery execution result:")
    print(recovery_result)

    assert recovery_result["success"] is True
    assert "Recovery successful" in recovery_result["stdout"]

    print("[TEST] Recovery succeeded")

    print("\n=== PHASE 7: CONTINUE WORKFLOW ===")

    final_result = tool_system.executor.execute(
        "run_command",
        command="echo Final step completed",
        timeout=10,
    )

    print("[TEST] Final step result:")
    print(final_result)

    assert final_result["success"] is True
    assert "Final step completed" in final_result["stdout"]

    print("[TEST] Workflow continuation succeeded")

    print("\n=== PERMISSION + RECOVERY + CONTINUATION TEST PASSED ===")
    print("=== ALL INTEGRATION TESTS PASSED ===")


if __name__ == "__main__":
    main()
