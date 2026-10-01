from core.executor.tool_system import ToolSystem
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)


def create_file(
    filename: str,
    content: str,
) -> str:

    return (
        f"Created {filename} "
        f"with {len(content)} characters"
    )


def open_browser(
    url: str,
) -> str:

    return f"Opened {url}"


def install_package(
    package: str,
) -> str:

    return f"Installed {package}"


def main():

    print("\n=== TOOL SYSTEM TEST ===\n")

    tool_system = ToolSystem()

    # ---------------------------------------------
    # Register tools
    # ---------------------------------------------

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
            name="open_browser",
            description="Open a webpage in the browser",
            risk=ToolRisk.LOW,
            parameters=[
                ToolParameter(
                    name="url",
                    description="Webpage URL",
                ),
            ],
        ),
        implementation=open_browser,
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

    print(
        "\n[TEST] Available tools:"
    )

    print(
        tool_system.available_tools()
    )

    # ---------------------------------------------
    # Tool selection
    # ---------------------------------------------

    print(
        "\n[TEST] Selecting tool for goal:"
    )

    goal = "Create a new file"

    selected = tool_system.find_tools(
        goal
    )

    print(
        f"[TEST] Goal: {goal}"
    )

    print(
        "[TEST] Selected:",
        [tool.name for tool in selected],
    )

    assert len(selected) == 1

    assert (
        selected[0].name
        == "create_file"
    )

    print(
        "[TEST] Correct tool selected"
    )

    # ---------------------------------------------
    # Safe execution
    # ---------------------------------------------

    print(
        "\n[TEST] Executing selected tool..."
    )

    result = tool_system.execute(
        task_id="tool-system-task",
        goal=goal,
        filename="hello.txt",
        content="Hello Converted OS!",
    )

    print(
        f"[TEST] Result: {result}"
    )

    assert (
        result["status"]
        == "allow"
    )

    assert (
        result["result"]
        == "Created hello.txt with 19 characters"
    )

    print(
        "[TEST] Tool executed successfully"
    )

    # ---------------------------------------------
    # Medium-risk permission test
    # ---------------------------------------------

    print(
        "\n[TEST] Testing medium-risk tool..."
    )

    result = tool_system.execute(
        task_id="install-task",
        goal="Install a software package",
        package="requests",
    )

    print(
        f"[TEST] Result: {result}"
    )

    assert (
        result["status"]
        == "pending"
    )

    print(
        "[TEST] Medium-risk tool correctly "
        "requires permission"
    )

    print(
        "\n=== TOOL SYSTEM TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
