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


def main():

    print(
        "\n=== TERMINAL TOOL TEST ===\n"
    )

    workspace = (
        "workspace/terminal_test"
    )

    Path(workspace).mkdir(
        parents=True,
        exist_ok=True,
    )

    terminal = TerminalTools(
        workspace=workspace
    )

    tool_system = ToolSystem()

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

    print(
        "[TEST] Terminal tool registered"
    )

    result = tool_system.execute(
        task_id="terminal-test",
        goal="run command",
        command="echo Converted OS",
        timeout=10,
    )

    print(
        "\n[TEST] Result:"
    )

    print(result)

    assert result["status"] == "pending"

    print(
        "\n[TEST] Medium-risk terminal "
        "operation correctly requires permission"
    )

    print(
        "\n=== TERMINAL TOOL TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
