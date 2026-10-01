from pathlib import Path

from core.agent.tool_agent import ToolAgent
from core.agent.tool_planning_agent import ToolPlanningAgent
from core.agent.verified_tool_agent import VerifiedToolAgent

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

from core.observer.file_observer import FileObserver


class FakeAIModel(AIModel):

    def generate(
        self,
        prompt: str,
    ) -> str:

        print(
            "\n[FAKE AI] Generating plan"
        )

        return """
{
    "goal": "Create verified.txt",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "verified.txt",
                "content": "Converted OS verification works!"
            }
        }
    ]
}
"""


def main():

    print(
        "\n=== VERIFIED TOOL AGENT TEST ===\n"
    )

    workspace = (
        "workspace/verified_agent"
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

    ai_model = FakeAIModel()

    tool_agent = ToolAgent(
        ai_model=ai_model,
        discovery=discovery,
        executor=executor,
    )

    file_observer = FileObserver()

    agent = VerifiedToolAgent(
        tool_agent=tool_agent,
        file_observer=file_observer,
    )

    goal = (
        "Create verified.txt"
    )

    expected_file = (
        Path(workspace)
        / "verified.txt"
    )

    expected_content = (
        "Converted OS verification works!"
    )

    result = agent.run(
        task_id="verified-task",
        goal=goal,
        expected_file=str(expected_file),
        expected_content=expected_content,
    )

    print(
        "\n[TEST] Final result:"
    )

    print(result)

    assert result["success"] is True
    assert result["verified"] is True
    assert expected_file.exists()

    print(
        "\n[TEST] Agent action was "
        "successfully verified"
    )

    print(
        "\n=== VERIFIED TOOL AGENT "
        "TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
