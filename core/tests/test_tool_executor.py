from core.executor.tool_executor import ToolExecutor
from core.executor.tool_registry import ToolRegistry


def create_file(
    filename: str,
    content: str,
) -> str:

    return (
        f"Created {filename} "
        f"with {len(content)} characters"
    )


def main():

    print("\n=== TOOL EXECUTOR TEST ===\n")

    registry = ToolRegistry()

    registry.register(
        name="create_file",
        tool=create_file,
    )

    executor = ToolExecutor(
        registry=registry
    )

    # Execute a registered tool
    result = executor.execute(
        "create_file",
        filename="hello.txt",
        content="Hello Converted OS!",
    )

    print(
        f"[TEST] Result: {result}"
    )

    assert (
        result
        == "Created hello.txt with 19 characters"
    )

    print(
        "[TEST] Registered tool executed successfully"
    )

    # Unknown tool must fail
    try:

        executor.execute(
            "unknown_tool"
        )

        raise AssertionError(
            "Unknown tool was not rejected"
        )

    except ValueError as error:

        print(
            f"[TEST] Unknown tool rejected: "
            f"{error}"
        )

    registry.unregister(
        "create_file"
    )

    print(
        "\n=== TOOL EXECUTOR TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
