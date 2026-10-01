from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_definition import (
    ToolDefinition,
    ToolRisk,
)
from core.executor.tool_selector import ToolSelector


def create_file(filename: str, content: str):
    return f"Created {filename}"


def read_file(filename: str):
    return f"Contents of {filename}"


def open_browser(url: str):
    return f"Opened {url}"


def main():

    print("\n=== TOOL SELECTOR TEST ===\n")

    catalog = ToolCatalog()

    catalog.register(
        ToolDefinition(
            name="create_file",
            description="Create a new file",
            risk=ToolRisk.LOW,
        ),
        create_file,
    )

    catalog.register(
        ToolDefinition(
            name="read_file",
            description="Read an existing file",
            risk=ToolRisk.LOW,
        ),
        read_file,
    )

    catalog.register(
        ToolDefinition(
            name="open_browser",
            description="Open a webpage in the browser",
            risk=ToolRisk.MEDIUM,
        ),
        open_browser,
    )

    selector = ToolSelector(catalog)

    # Test file creation goal
    selected = selector.select(
        "Create a new file"
    )

    names = [
        tool.name
        for tool in selected
    ]

    print(
        f"[TEST] Goal: Create a new file"
    )

    print(
        f"[TEST] Selected tools: {names}"
    )

    assert "create_file" in names

    # Test browser goal
    selected = selector.select(
        "Open a webpage in the browser"
    )

    names = [
        tool.name
        for tool in selected
    ]

    print(
        f"\n[TEST] Goal: Open a webpage in the browser"
    )

    print(
        f"[TEST] Selected tools: {names}"
    )

    assert "open_browser" in names

    # Test unknown goal
    selected = selector.select(
        "Make breakfast"
    )

    print(
        f"\n[TEST] Goal: Make breakfast"
    )

    print(
        f"[TEST] Selected tools: "
        f"{[tool.name for tool in selected]}"
    )

    assert selected == []

    print(
        "\n[TEST] Unknown goal correctly returned no tools"
    )

    print(
        "\n=== TOOL SELECTOR TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
