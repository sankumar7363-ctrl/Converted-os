from pathlib import Path

from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)

from core.executor.tool_system import ToolSystem

from core.executor.tools.terminal_tools import (
    TerminalTools,
)


def register_terminal_tool(
    tool_system: ToolSystem,
    workspace: str,
):

    terminal = TerminalTools(
        workspace=workspace
    )

    tool_system.register(
        definition=ToolDefinition(
            name="run_command",
            description=(
                "Execute a terminal command "
                "inside the Converted OS workspace"
            ),
            risk=ToolRisk.MEDIUM,
            parameters=[
                ToolParameter(
                    name="command",
                    description=(
                        "Terminal command to execute"
                    ),
                ),
                ToolParameter(
                    name="timeout",
                    description=(
                        "Maximum execution time in seconds"
                    ),
                    required=False,
                ),
            ],
        ),
        implementation=terminal.run_command,
    )


def main():

    print(
        "\n=== TERMINAL APPROVAL TEST ===\n"
    )

    workspace = (
        "workspace/terminal_approval"
    )

    Path(workspace).mkdir(
        parents=True,
        exist_ok=True,
    )

    tool_system = ToolSystem()

    register_terminal_tool(
        tool_system,
        workspace,
    )

    task_id = "terminal-approval-test"

    print(
        "\n[TEST] Requesting terminal execution"
    )

    pending = tool_system.execute(
        task_id=task_id,
        goal="run command",
        command="echo Converted OS",
        timeout=10,
    )

    print(
        "\n[TEST] Pending result:"
    )

    print(pending)

    assert pending["status"] == "pending"

    assert (
        tool_system.permissions.is_pending(
            task_id
        )
    )

    print(
        "\n[TEST] Permission request verified"
    )

    print(
        "\n[TEST] Approving terminal command"
    )

    approved = (
        tool_system.permissions.approve(
            task_id
        )
    )

    assert approved is True

    print(
        "[TEST] Permission approved"
    )

    result = (
        tool_system.executor.execute(
            "run_command",
            command="echo Converted OS",
            timeout=10,
        )
    )

    print(
        "\n[TEST] Terminal result:"
    )

    print(result)

    assert result["success"] is True

    assert (
        result["return_code"] == 0
    )

    assert (
        result["stdout"].strip()
        == "Converted OS"
    )

    assert result["stderr"] == ""

    print(
        "\n[TEST] stdout captured correctly"
    )

    print(
        "[TEST] Exit code captured correctly"
    )

    print(
        "[TEST] Terminal command executed "
        "only after approval"
    )

    print(
        "\n=== TERMINAL APPROVAL "
        "TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
