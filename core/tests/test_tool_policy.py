from core.executor.tool_definition import (
    ToolDefinition,
    ToolRisk,
)
from core.executor.tool_policy import ToolPolicy
from core.policy.policy import PolicyDecision


def main():

    print("\n=== TOOL POLICY TEST ===\n")

    policy = ToolPolicy()

    # LOW-risk tool
    low_tool = ToolDefinition(
        name="create_file",
        description="Create a file in the workspace",
        risk=ToolRisk.LOW,
    )

    low_result = policy.evaluate(
        low_tool
    )

    print(
        f"[TEST] LOW decision: "
        f"{low_result.decision.value}"
    )

    assert (
        low_result.decision
        == PolicyDecision.ALLOW
    )

    # MEDIUM-risk tool
    medium_tool = ToolDefinition(
        name="install_package",
        description="Install a software package",
        risk=ToolRisk.MEDIUM,
    )

    medium_result = policy.evaluate(
        medium_tool
    )

    print(
        f"[TEST] MEDIUM decision: "
        f"{medium_result.decision.value}"
    )

    assert (
        medium_result.decision
        == PolicyDecision.ASK
    )

    # HIGH-risk tool
    high_tool = ToolDefinition(
        name="format_disk",
        description="Format a disk",
        risk=ToolRisk.HIGH,
    )

    high_result = policy.evaluate(
        high_tool
    )

    print(
        f"[TEST] HIGH decision: "
        f"{high_result.decision.value}"
    )

    assert (
        high_result.decision
        == PolicyDecision.BLOCK
    )

    print(
        "\n[TEST] All risk levels mapped correctly"
    )

    print(
        "\n=== TOOL POLICY TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
