from core.executor.tool_registry import ToolRegistry


def create_test_file(
    filename: str,
    content: str,
) -> str:

    print(
        f"[TEST TOOL] Creating: {filename}"
    )

    return (
        f"Created {filename} "
        f"with {len(content)} characters"
    )


def main():

    print("\n=== TOOL REGISTRY TEST ===\n")

    registry = ToolRegistry()

    # Register a tool.
    registry.register(
        "create_test_file",
        create_test_file,
    )

    # Verify registration.
    assert registry.has(
        "create_test_file"
    )

    print(
        "[TEST] Tool registered successfully"
    )

    # List tools.
    tools = registry.list_tools()

    print(
        f"[TEST] Registered tools: {tools}"
    )

    assert tools == [
        "create_test_file"
    ]

    # Execute the tool.
    result = registry.execute(
        "create_test_file",
        filename="hello.txt",
        content="Hello Converted OS!",
    )

    print(
        f"[TEST] Result: {result}"
    )

    assert result == (
        "Created hello.txt "
        "with 19 characters"
    )

    print(
        "[TEST] Tool executed successfully"
    )

    # Unknown tool should fail.
    try:

        registry.execute(
            "unknown_tool"
        )

        raise AssertionError(
            "Unknown tool should have failed"
        )

    except ValueError as error:

        print(
            f"[TEST] Unknown tool rejected: "
            f"{error}"
        )

    # Unregister tool.
    removed = registry.unregister(
        "create_test_file"
    )

    assert removed

    assert not registry.has(
        "create_test_file"
    )

    print(
        "[TEST] Tool unregistered successfully"
    )

    print(
        "\n=== TOOL REGISTRY TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
