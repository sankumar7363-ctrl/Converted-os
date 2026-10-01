from core.executor.tool_plan_executor import (
    ToolPlanExecutor,
)

from core.executor.tool_system import (
    ToolSystem,
)

from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)

from core.models.tool_call import (
    ToolCall,
    ToolPlan,
)


executed_tools = []


def create_file(
    filename: str,
    content: str,
) -> str:

    executed_tools.append(
        f"create_file:{filename}"
    )

    return f"Created {filename}"


def install_package(
    package: str,
) -> str:

    executed_tools.append(
        f"install_package:{package}"
    )

    return f"Installed {package}"


def main():

    print(
        "\n=== TOOL PLAN VALIDATION + RESUME TEST ===\n"
    )

    tool_system = ToolSystem()

    # -----------------------------------------
    # Register tools
    # -----------------------------------------

    tool_system.register(
        definition=ToolDefinition(
            name="create_file",
            description="Create a file",
            risk=ToolRisk.LOW,
            parameters=[
                ToolParameter(
                    name="filename",
                    description="File name",
                ),
                ToolParameter(
                    name="content",
                    description="File content",
                ),
            ],
        ),
        implementation=create_file,
    )

    tool_system.register(
        definition=ToolDefinition(
            name="install_package",
            description="Install a software package",
            risk=ToolRisk.MEDIUM,
            parameters=[
                ToolParameter(
                    name="package",
                    description="Package name",
                ),
            ],
        ),
        implementation=install_package,
    )

    executor = ToolPlanExecutor(
        tool_system=tool_system
    )

    # -----------------------------------------
    # Valid plan
    # -----------------------------------------

    plan = ToolPlan(
        goal="Create a file and install a package",
        calls=[
            ToolCall(
                tool_name="create_file",
                arguments={
                    "filename": "hello.txt",
                    "content": "Hello Converted OS!",
                },
            ),
            ToolCall(
                tool_name="install_package",
                arguments={
                    "package": "requests",
                },
            ),
        ],
    )

    task_id = "validation-task"

    print(
        "[TEST] Executing valid plan..."
    )

    results = executor.execute(
        task_id=task_id,
        plan=plan,
    )

    assert (
        "create_file:hello.txt"
        in executed_tools
    )

    assert (
        "install_package:requests"
        not in executed_tools
    )

    assert (
        results[-1]["status"]
        == "pending"
    )

    print(
        "[TEST] Valid plan executed "
        "and paused correctly"
    )

    # -----------------------------------------
    # Approve pending action
    # -----------------------------------------

    print(
        "\n[TEST] Approving pending action..."
    )

    resumed = executor.approve_pending(
        task_id
    )

    assert (
        "install_package:requests"
        in executed_tools
    )

    assert (
        task_id
        not in executor.pending_plans
    )

    assert (
        task_id
        not in executor.pending_indexes
    )

    print(
        "[TEST] Approved action executed"
    )

    print(
        "[TEST] Pending state cleared"
    )

    # -----------------------------------------
    # Invalid plan: missing argument
    # -----------------------------------------

    print(
        "\n[TEST] Testing missing argument..."
    )

    invalid_missing = ToolPlan(
        goal="Invalid missing argument",
        calls=[
            ToolCall(
                tool_name="create_file",
                arguments={
                    "filename": "bad.txt",
                },
            ),
        ],
    )

    try:

        executor.execute(
            task_id="invalid-missing",
            plan=invalid_missing,
        )

        raise AssertionError(
            "Missing argument was not rejected"
        )

    except ValueError as error:

        print(
            f"[TEST] Correctly rejected: {error}"
        )

    # -----------------------------------------
    # Invalid plan: unknown argument
    # -----------------------------------------

    print(
        "\n[TEST] Testing unknown argument..."
    )

    invalid_unknown = ToolPlan(
        goal="Invalid unknown argument",
        calls=[
            ToolCall(
                tool_name="create_file",
                arguments={
                    "filename": "bad.txt",
                    "content": "Bad",
                    "unknown": "value",
                },
            ),
        ],
    )

    try:

        executor.execute(
            task_id="invalid-unknown",
            plan=invalid_unknown,
        )

        raise AssertionError(
            "Unknown argument was not rejected"
        )

    except ValueError as error:

        print(
            f"[TEST] Correctly rejected: {error}"
        )

    # -----------------------------------------
    # Invalid plan: unknown tool
    # -----------------------------------------

    print(
        "\n[TEST] Testing unknown tool..."
    )

    invalid_tool = ToolPlan(
        goal="Invalid tool",
        calls=[
            ToolCall(
                tool_name="does_not_exist",
                arguments={},
            ),
        ],
    )

    try:

        executor.execute(
            task_id="invalid-tool",
            plan=invalid_tool,
        )

        raise AssertionError(
            "Unknown tool was not rejected"
        )

    except ValueError as error:

        print(
            f"[TEST] Correctly rejected: {error}"
        )

    print(
        "\n=== TOOL PLAN VALIDATION + RESUME TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
