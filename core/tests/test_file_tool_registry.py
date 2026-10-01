from core.executor.tool_registry import ToolRegistry
from tools.file_tool import FileTool


def main():

    print("\n=== FILE TOOL REGISTRY TEST ===\n")

    registry = ToolRegistry()

    file_tool = FileTool(
        workspace="workspace/test_registry"
    )

    registry.register(
        "create_file",
        file_tool.create_file,
    )

    registry.register(
        "read_file",
        file_tool.read_file,
    )

    print(
        f"[TEST] Tools: "
        f"{registry.list_tools()}"
    )

    # Create a file through the registry.
    result = registry.execute(
        "create_file",
        filename="hello.txt",
        content="Hello from Converted OS!",
    )

    print(
        f"[TEST] Created: {result}"
    )

    # Read the same file through the registry.
    content = registry.execute(
        "read_file",
        filename="hello.txt",
    )

    print(
        f"[TEST] Read content: {content}"
    )

    assert content == (
        "Hello from Converted OS!"
    )

    print(
        "[TEST] File creation and reading "
        "worked through Tool Registry"
    )

    print(
        "\n=== FILE TOOL REGISTRY TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
