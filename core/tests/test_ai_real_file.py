from pathlib import Path

from core.agent.tool_agent import ToolAgent
from core.ai.model import AIModel

from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)
from core.executor.tool_discovery import ToolDiscovery
from core.executor.tool_plan_executor import ToolPlanExecutor
from core.executor.tool_system import ToolSystem
from core.executor.tools.file_tools import FileTools


class FakeAIModel(AIModel):

    def generate(
        self,
        prompt: str,
    ) -> str:

        print(
            "\n[FAKE AI] Creating tool plan..."
        )

        return """
{
    "goal": "Create a file called converted.txt",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "converted.txt",
                "content": "Converted OS is working!"
            }
        }
    ]
}
"""


def main():

    print(
        "\n=== AI → REAL FILESYSTEM TEST ===\n"
    )

    workspace = "workspace/ai_real_file"

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

    ai_model = FakeAIModel()

    agent = ToolAgent(
        ai_model=ai_model,
        discovery=discovery,
        executor=executor,
    )

    goal = (
        "Create a file called converted.txt"
    )

    print(
        f"[TEST] User goal: {goal}"
    )

    results = agent.run(
        task_id="ai-real-file-task",
        goal=goal,
    )

    print(
        "\n[TEST] Final results:"
    )

    print(results)

    file_path = (
        Path(workspace)
        / "converted.txt"
    )

    assert file_path.exists()

    print(
        f"[TEST] File exists: {file_path}"
    )

    content = file_path.read_text(
        encoding="utf-8"
    )

    print(
        f"[TEST] File content: {content}"
    )

    assert (
        content
        == "Converted OS is working!"
    )

    assert len(results) == 1

    assert (
        results[0]["status"]
        == "allow"
    )

    assert (
        results[0]["tool"]
        == "create_file"
    )

    print(
        "\n[TEST] AI successfully caused "
        "a real filesystem action"
    )

    print(
        "\n=== AI → REAL FILESYSTEM "
        "TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
