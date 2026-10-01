from pathlib import Path

from core.ai.model import AIModel

from core.agent.tool_agent import ToolAgent

from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)

from core.executor.tool_discovery import ToolDiscovery
from core.executor.tool_plan_executor import ToolPlanExecutor
from core.executor.tool_system import ToolSystem
from core.executor.tools.file_tools import FileTools


class FakeMultiStepAI(AIModel):

    def generate(
        self,
        prompt: str,
    ) -> str:

        print(
            "\n[FAKE AI] Generating multi-step plan"
        )

        return """
{
    "goal": "Create a simple website",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "index.html",
                "content": "<html><body><h1>Converted OS</h1></body></html>"
            }
        },
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "style.css",
                "content": "body { font-family: sans-serif; }"
            }
        },
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "README.md",
                "content": "# Converted OS Website"
            }
        }
    ]
}
"""


def main():

    print(
        "\n=== MULTI-STEP TOOL AGENT TEST ===\n"
    )

    workspace = (
        "workspace/multi_step_test"
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

    discovery = ToolDiscovery(
        catalog=tool_system.catalog
    )

    executor = ToolPlanExecutor(
        tool_system=tool_system
    )

    ai_model = FakeMultiStepAI()

    agent = ToolAgent(
        ai_model=ai_model,
        discovery=discovery,
        executor=executor,
    )

    goal = "Create a simple website"

    results = agent.run(
        task_id="multi-step-task",
        goal=goal,
    )

    print(
        "\n[TEST] Final results:"
    )

    print(results)

    expected_files = [
        "index.html",
        "style.css",
        "README.md",
    ]

    for filename in expected_files:

        filepath = (
            Path(workspace)
            / filename
        )

        assert filepath.exists()

        print(
            f"[TEST] Verified file: {filepath}"
        )

    assert len(results) == 3

    for result in results:

        assert (
            result["status"]
            == "allow"
        )

        assert (
            result["tool"]
            == "create_file"
        )

    print(
        "\n[TEST] All three tool calls "
        "executed successfully"
    )

    print(
        "\n=== MULTI-STEP TOOL AGENT "
        "TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
