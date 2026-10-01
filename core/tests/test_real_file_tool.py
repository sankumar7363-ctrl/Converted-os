from pathlib import Path

from core.executor.tool_system import ToolSystem
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)

from core.executor.tools.file_tools import (
    FileTools,
)


def main():

    print(
        "\n=== REAL FILE TOOL TEST ===\n"
    )

    workspace = "workspace/test_real_file_tool"

    file_tools = FileTools(
        workspace=workspace
    )

    tool_system = ToolSystem()

    tool_system.register(
        definition=ToolDefinition(
            name="create_file",
            description="Create a file in the workspace",
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
        implementation=file_tools.create_file,
    )

    tool_system.register(
        definition=ToolDefinition(
            name="read_file",
            description="Read a file from the workspace",
            risk=ToolRisk.LOW,
            parameters=[
                ToolParameter(
                    name="filename",
                    description="File name",
                ),
            ],
        ),
        implementation=file_tools.read_file,
    )

    print(
        "[TEST] Creating real file..."
    )

    result = tool_system.safe_executor.execute(
        task_id="real-file-task",
        tool_name="create_file",
        filename="hello.txt",
        content="Hello from Converted OS!",
    )

    print(
        f"[TEST] Create result: {result}"
    )

    file_path = Path(
        workspace
    ) / "hello.txt"

    assert file_path.exists()

    print(
        "[TEST] Real file exists"
    )

    print(
        "[TEST] Reading real file..."
    )

    read_result = tool_system.safe_executor.execute(
        task_id="real-file-read-task",
        tool_name="read_file",
        filename="hello.txt",
    )

    print(
        f"[TEST] Read result: {read_result}"
    )

    assert (
        read_result["result"]
        == "Hello from Converted OS!"
    )

    print(
        "\n[TEST] Real filesystem tool works"
    )

    print(
        "\n=== REAL FILE TOOL TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
