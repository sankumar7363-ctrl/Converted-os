from core.models.tool_result import ToolResultStatus

from core.ai.model import AIModel

from core.executor.recovery_tool_plan_executor import (
    RecoveryToolPlanExecutor,
)

from core.executor.tool_system import ToolSystem

from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)

from core.executor.tools.terminal_tools import (
    TerminalTools,
)

from core.models.tool_call import (
    ToolCall,
    ToolPlan,
)


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
""".strip()

def get_stdout(observation):
    result = observation.result

    if not isinstance(result, dict):
        return ""

    # Raw tool result
    if "stdout" in result:
        return result.get("stdout", "")

    # Safe-executor wrapped result
    nested = result.get("result")

    if isinstance(nested, dict):
        return nested.get("stdout", "")

    return ""

def main():

    print("\n=== STATEFUL RECOVERY RESUME TEST ===")

    # ---------------------------------------------------------
    # TOOL SYSTEM
    # ---------------------------------------------------------

    tool_system = ToolSystem()

    terminal = TerminalTools()

    definition = ToolDefinition(
        name="run_command",
        description=(
            "Run a terminal command inside the workspace"
        ),
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
                default=10,
            ),
        ],
    )

    tool_system.register(
        definition,
        terminal.run_command,
    )

    ai_model = FakeRecoveryAI()

    executor = RecoveryToolPlanExecutor(
        tool_system=tool_system,
        ai_model=ai_model,
    )

    task_id = "stateful-recovery-test"

    # ---------------------------------------------------------
    # ORIGINAL PLAN
    # ---------------------------------------------------------

    plan = ToolPlan(
        goal="Execute a stateful recovery workflow",
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

    # ---------------------------------------------------------
    # PHASE 1
    # ---------------------------------------------------------

    print("\n=== PHASE 1: INITIAL EXECUTION ===")

    observations = executor.execute(
        task_id=task_id,
        plan=plan,
    )

    assert len(observations) == 1

    first = observations[0]

    assert first.status.value == "pending_permission"
    assert first.success is False

    print(
        "[TEST] Initial execution correctly paused "
        "for permission"
    )

    # ---------------------------------------------------------
    # PHASE 2
    # ---------------------------------------------------------

    print("\n=== PHASE 2: VERIFY PAUSED STATE ===")

    assert task_id in executor.pending_tasks
    assert task_id in executor.pending_indexes

    assert executor.pending_tasks[task_id] == plan
    assert executor.pending_indexes[task_id] == 0

    print("[TEST] Task state stored correctly")
    print(
        f"[TEST] Pending step: "
        f"{executor.pending_indexes[task_id]}"
    )

    # ---------------------------------------------------------
    # PHASE 3
    # ---------------------------------------------------------

    print("\n=== PHASE 3: RESUME ORIGINAL STEP ===")

    resumed_observations = executor.resume(
        task_id
    )

    assert resumed_observations is not None
    assert len(resumed_observations) == 2

    original_failure = resumed_observations[0]

    recovery_pending = resumed_observations[1]

    assert original_failure.success is False
    assert original_failure.status.value == "failure"

    assert (
        recovery_pending.status.value
        == "pending_permission"
    )

    print(
        "[TEST] Original step executed and failed"
    )

    print(
        "[TEST] Recovery action correctly requested "
        "permission"
    )

    # ---------------------------------------------------------
    # VERIFY RECOVERY STATE
    # ---------------------------------------------------------

    print("\n=== PHASE 4: VERIFY RECOVERY PAUSED STATE ===")

    assert task_id in executor.pending_tasks
    assert task_id in executor.pending_recovery_calls
    assert task_id in executor.pending_recovery_indexes

    recovery_call = (
        executor.pending_recovery_calls[task_id]
    )

    assert recovery_call.tool_name == "run_command"

    assert (
        recovery_call.arguments["command"]
        == "echo Recovery successful"
    )

    print(
        "[TEST] Recovery action stored correctly"
    )

    print(
        "[TEST] Recovery command:",
        recovery_call.arguments["command"],
    )

    # ---------------------------------------------------------
    # PHASE 5
    # ---------------------------------------------------------

    print("\n=== PHASE 5: RESUME RECOVERY ACTION ===")

    recovery_observations = executor.resume(
        task_id
    )

    assert recovery_observations is not None

    print(
        "[TEST] Recovery resume observations:"
    )

    for observation in recovery_observations:

        print(
            f"step_index={observation.step_index} "
            f"tool_name={observation.tool_name} "
            f"status={observation.status} "
            f"success={observation.success}"
        )

    # ---------------------------------------------------------
    # VERIFY RECOVERY SUCCESS
    # ---------------------------------------------------------

    print("\n=== PHASE 6: VERIFY RECOVERY SUCCESS ===")

    recovery_success = any(
        observation.success
        and observation.tool_name == "run_command"
        and get_stdout(observation).strip() == "Recovery successful"
        for observation in recovery_observations
    )

    assert recovery_success
    print("[TEST] Recovery action executed successfully")

    # ---------------------------------------------------------
    # VERIFY FINAL STEP PAUSED
    # ---------------------------------------------------------

    print(
        "\n=== PHASE 7: VERIFY FINAL STEP PAUSED ==="
    )

    final_step_pending = any(
        observation.status == ToolResultStatus.PENDING_PERMISSION
        and observation.tool_name == "run_command"
        for observation in recovery_observations
    )

    assert final_step_pending
    print("[TEST] Final step correctly requested permission")

    # ---------------------------------------------------------
    # RESUME FINAL STEP
    # ---------------------------------------------------------

    print("\n=== PHASE 8: RESUME FINAL STEP ===")

    final_observations = executor.resume(task_id)

    assert final_observations is not None

    print("[TEST] Final-step resume observations:")

    for observation in final_observations:
        print(
            f"step_index={observation.step_index} "
            f"tool_name={observation.tool_name} "
            f"status={observation.status} "
            f"success={observation.success}"
        )

    final_step_success = any(
        observation.success
        and observation.tool_name == "run_command"
        and get_stdout(observation).strip() == "Final step completed"
        for observation in final_observations
    )

    assert final_step_success
    print("[TEST] Final step executed successfully")

    # ---------------------------------------------------------
    # VERIFY CLEANUP
    # ---------------------------------------------------------

    print(
        "\n=== PHASE 9: VERIFY STATE CLEANUP ==="
    )

    assert task_id not in executor.pending_tasks
    assert task_id not in executor.pending_indexes
    assert task_id not in executor.pending_recovery_calls
    assert task_id not in executor.pending_recovery_indexes

    print(
        "[TEST] All pending task state cleaned up"
    )

    print(
        "\n=== STATEFUL RECOVERY RESUME TEST PASSED ==="
    )

    print(
        "=== PAUSE → RESUME → FAILURE → RECOVERY "
        "→ RESUME → CONTINUATION → RESUME PASSED ==="
    )

if __name__ == "__main__":
    main()
