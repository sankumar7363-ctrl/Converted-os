from pathlib import Path

from core.ai.model import AIModel

from core.executor.recovery_tool_plan_executor import (
    RecoveryToolPlanExecutor,
)

from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)

from core.executor.tool_system import ToolSystem

from core.executor.tool_plan_parser import (
    ToolPlanParser,
)

from core.executor.tools.file_tools import (
    FileTools,
)

from core.observer.tool_observer import (
    ToolObserver,
)


class FakeRecoveryAI(AIModel):

    def generate(
        self,
        prompt: str,
    ) -> str:

        if "recovery planner" in prompt.lower():

            print(
                "[FAKE AI] Generating recovery plan"
            )

            return """
{
    "goal": "Recovery for failed step",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "style.css",
                "content": "body { margin: 0; }"
            }
        }
    ]
}
"""

        return """
{
    "goal": "Create a website",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "index.html",
                "content": "<html>Converted OS</html>"
            }
        },
        {
            "tool_name": "missing_tool",
            "arguments": {}
        },
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "README.md",
                "content": "# Converted OS"
            }
        }
    ]
}
"""


def main():

    print(
        "\n=== TARGETED RECOVERY TEST ===\n"
    )

    workspace = (
        "workspace/targeted_recovery"
    )

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

    ai = FakeRecoveryAI()

    parser = ToolPlanParser()

    plan = parser.parse(
        ai.generate(
            "Create a website"
        )
    )

    observer = ToolObserver()

    executor = RecoveryToolPlanExecutor(
        tool_system=tool_system,
        ai_model=ai,
        observer=observer,
    )

    results = executor.execute(
        task_id="recovery-task",
        plan=plan,
    )

    print(
        "\n[TEST] Final observations:"
    )

    for result in results:
        print(result)

    index_file = (
        Path(workspace)
        / "index.html"
    )

    style_file = (
        Path(workspace)
        / "style.css"
    )

    readme_file = (
        Path(workspace)
        / "README.md"
    )

    assert index_file.exists()
    assert style_file.exists()
    assert readme_file.exists()

    assert (
        index_file.read_text(
            encoding="utf-8"
        )
        == "<html>Converted OS</html>"
    )

    assert (
        style_file.read_text(
            encoding="utf-8"
        )
        == "body { margin: 0; }"
    )

    assert (
        readme_file.read_text(
            encoding="utf-8"
        )
        == "# Converted OS"
    )

    print(
        "\n[TEST] Step 1 completed"
    )

    print(
        "[TEST] Step 2 failed"
    )

    print(
        "[TEST] Step 2 recovered successfully"
    )

    print(
        "[TEST] Step 3 continued successfully"
    )

    print(
        "\n=== TARGETED RECOVERY "
        "TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
