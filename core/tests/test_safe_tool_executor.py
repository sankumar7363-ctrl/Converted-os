from core.executor.safe_tool_executor import SafeToolExecutor
from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_definition import (
    ToolDefinition,
    ToolRisk,
)
from core.executor.tool_executor import ToolExecutor
from core.executor.tool_policy import ToolPolicy
from core.executor.tool_registry import ToolRegistry


executed_tools = []


def low_risk_tool():

    executed_tools.append(
        "low_risk_tool"
    )

    return "Low-risk tool executed"


def medium_risk_tool():

    executed_tools.append(
        "medium_risk_tool"
    )

    return "Medium-risk tool executed"


def high_risk_tool():

    executed_tools.append(
        "high_risk_tool"
    )

    return "High-risk tool executed"


def register_tool(
    catalog,
    registry,
    name,
    description,
    risk,
    implementation,
):

    registry.register(
        name=name,
        tool=implementation,
    )

    catalog.register(
        definition=ToolDefinition(
            name=name,
            description=description,
            risk=risk,
        ),
        implementation=implementation,
    )


def main():

    print(
        "\n=== SAFE TOOL EXECUTOR TEST ===\n"
    )

    registry = ToolRegistry()

    catalog = ToolCatalog()

    register_tool(
        catalog,
        registry,
        "low_risk_tool",
        "Create a simple file",
        ToolRisk.LOW,
        low_risk_tool,
    )

    register_tool(
        catalog,
        registry,
        "medium_risk_tool",
        "Install a package",
        ToolRisk.MEDIUM,
        medium_risk_tool,
    )

    register_tool(
        catalog,
        registry,
        "high_risk_tool",
        "Format disk",
        ToolRisk.HIGH,
        high_risk_tool,
    )

    executor = ToolExecutor(
        registry=registry
    )

    safe_executor = SafeToolExecutor(
        catalog=catalog,
        executor=executor,
        policy=ToolPolicy(),
    )

    # ------------------------------------------------
    # LOW-RISK TEST
    # ------------------------------------------------

    print(
        "\n[TEST] Testing LOW-risk tool..."
    )

    result = safe_executor.execute(
        task_id="task-low",
        tool_name="low_risk_tool",
    )

    print(
        f"[TEST] Result: {result}"
    )

    assert (
        result["status"]
        == "allow"
    )

    assert (
        "low_risk_tool"
        in executed_tools
    )

    print(
        "[TEST] LOW-risk tool executed"
    )

    # ------------------------------------------------
    # MEDIUM-RISK TEST
    # ------------------------------------------------

    print(
        "\n[TEST] Testing MEDIUM-risk tool..."
    )

    result = safe_executor.execute(
        task_id="task-medium",
        tool_name="medium_risk_tool",
    )

    print(
        f"[TEST] Result: {result}"
    )

    assert (
        result["status"]
        == "pending"
    )

    assert (
        "medium_risk_tool"
        not in executed_tools
    )

    print(
        "[TEST] MEDIUM-risk tool correctly "
        "paused for permission"
    )

    # ------------------------------------------------
    # HIGH-RISK TEST
    # ------------------------------------------------

    print(
        "\n[TEST] Testing HIGH-risk tool..."
    )

    try:

        safe_executor.execute(
            task_id="task-high",
            tool_name="high_risk_tool",
        )

        raise AssertionError(
            "HIGH-risk tool was not blocked"
        )

    except PermissionError as error:

        print(
            f"[TEST] HIGH-risk tool blocked: "
            f"{error}"
        )

    assert (
        "high_risk_tool"
        not in executed_tools
    )

    print(
        "[TEST] HIGH-risk tool correctly blocked"
    )

    # ------------------------------------------------
    # UNKNOWN TOOL TEST
    # ------------------------------------------------

    print(
        "\n[TEST] Testing unknown tool..."
    )

    try:

        safe_executor.execute(
            task_id="task-unknown",
            tool_name="unknown_tool",
        )

        raise AssertionError(
            "Unknown tool was not rejected"
        )

    except ValueError as error:

        print(
            f"[TEST] Unknown tool rejected: "
            f"{error}"
        )

    print(
        "\n=== SAFE TOOL EXECUTOR TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
