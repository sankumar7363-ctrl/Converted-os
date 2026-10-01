from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)
from core.executor.tool_discovery import ToolDiscovery


def create_file(
    filename: str,
    content: str,
) -> str:

    return f"Created {filename}"


def main():

    print("\n=== TOOL DISCOVERY TEST ===\n")

    catalog = ToolCatalog()

    definition = ToolDefinition(
        name="create_file",
        description="Create a file inside the workspace",
        risk=ToolRisk.LOW,
        parameters=[
            ToolParameter(
                name="filename",
                description="Name of the file",
            ),
            ToolParameter(
                name="content",
                description="Content of the file",
            ),
        ],
        autonomous=True,
    )

    catalog.register(
        definition=definition,
        implementation=create_file,
    )

    discovery = ToolDiscovery(
        catalog=catalog
    )

    # Discover all tools
    tools = discovery.list_tools()

    print(
        f"[TEST] Discovered tools: "
        f"{[tool.name for tool in tools]}"
    )

    assert len(tools) == 1
    assert tools[0].name == "create_file"

    # Find a specific tool
    found = discovery.find_tool(
        "create_file"
    )

    assert found is not None

    print(
        f"[TEST] Found tool: {found.name}"
    )

    # Generate human/AI-readable description
    description = discovery.describe(
        "create_file"
    )

    assert description is not None

    print("\n[TEST] Tool description:")
    print(description)

    assert "create_file" in description
    assert "Create a file" in description
    assert "Risk: low" in description
    assert "Autonomous: True" in description
    assert "filename" in description
    assert "content" in description

    # Unknown tool
    unknown = discovery.find_tool(
        "unknown_tool"
    )

    assert unknown is None

    print(
        "\n[TEST] Unknown tool correctly not found"
    )

    unknown_description = discovery.describe(
        "unknown_tool"
    )

    assert unknown_description is None

    print(
        "[TEST] Unknown tool description correctly returned None"
    )

    catalog.unregister(
        "create_file"
    )

    print(
        "\n=== TOOL DISCOVERY TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
