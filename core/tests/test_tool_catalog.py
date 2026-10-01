from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)
from tools.file_tool import FileTool


def main():

    print("\n=== TOOL CATALOG TEST ===\n")

    catalog = ToolCatalog()

    file_tool = FileTool(
        workspace="workspace/test_catalog"
    )

    create_definition = ToolDefinition(
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
                description="Content to write",
            ),
        ],
        autonomous=True,
    )

    catalog.register(
        definition=create_definition,
        implementation=file_tool.create_file,
    )

    assert catalog.has("create_file")

    print(
        "[TEST] Tool registered successfully"
    )

    definition = catalog.get_definition(
        "create_file"
    )

    assert definition is not None

    print(
        f"[TEST] Name: {definition.name}"
    )

    print(
        f"[TEST] Description: "
        f"{definition.description}"
    )

    print(
        f"[TEST] Risk: "
        f"{definition.risk.value}"
    )

    print(
        f"[TEST] Autonomous: "
        f"{definition.autonomous}"
    )

    assert definition.risk == ToolRisk.LOW

    implementation = catalog.get_implementation(
        "create_file"
    )

    assert implementation is not None

    result = implementation(
        filename="catalog_test.txt",
        content="Hello from Tool Catalog!",
    )

    print(
        f"[TEST] File created: {result}"
    )

    tools = catalog.list_tools()

    print(
        f"[TEST] Available tools: {tools}"
    )

    assert tools == ["create_file"]

    descriptions = catalog.describe_tools()

    assert len(descriptions) == 1

    print(
        "[TEST] Tool description retrieved"
    )

    removed = catalog.unregister(
        "create_file"
    )

    assert removed

    assert not catalog.has(
        "create_file"
    )

    print(
        "[TEST] Tool removed successfully"
    )

    print(
        "\n=== TOOL CATALOG TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
