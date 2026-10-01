from pathlib import Path

from core.ai.model import AIModel
from core.agent.autonomous_tool_agent import AutonomousToolAgent
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)
from core.executor.tool_discovery import ToolDiscovery
from core.executor.tool_system import ToolSystem
from core.executor.tools.file_tools import FileTools


class FakeAutonomousAI(AIModel):

    def generate(self, prompt: str) -> str:

        if "recovery planner" in prompt.lower():
            print("[FAKE AI] Generating recovery plan")

            return """
{
    "goal": "Recover failed step",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "recovered.txt",
                "content": "Recovered successfully"
            }
        }
    ]
}
"""

        return """
{
    "goal": "Test autonomous execution",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "first.txt",
                "content": "First file"
            }
        },
        {
            "tool_name": "missing_tool",
            "arguments": {}
        },
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "last.txt",
                "content": "Last file"
            }
        }
    ]
}
"""


def main():

    print("\n=== AUTONOMOUS TOOL AGENT TEST ===\n")

    workspace = "workspace/autonomous_agent"

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

    ai = FakeAutonomousAI()

    agent = AutonomousToolAgent(
        ai_model=ai,
        discovery=discovery,
        tool_system=tool_system,
    )

    results = agent.run(
        task_id="autonomous-agent-test",
        goal="Test autonomous execution",
    )

    print("\n[TEST] Results:")

    for result in results:
        print(result)

    first_file = Path(workspace) / "first.txt"
    recovered_file = Path(workspace) / "recovered.txt"
    last_file = Path(workspace) / "last.txt"

    assert first_file.exists()
    assert recovered_file.exists()
    assert last_file.exists()

    assert first_file.read_text(
        encoding="utf-8"
    ) == "First file"

    assert recovered_file.read_text(
        encoding="utf-8"
    ) == "Recovered successfully"

    assert last_file.read_text(
        encoding="utf-8"
    ) == "Last file"

    print("\n[TEST] Initial action succeeded")
    print("[TEST] Failure detected")
    print("[TEST] Recovery action succeeded")
    print("[TEST] Remaining action continued")
    print("\n=== AUTONOMOUS TOOL AGENT TEST PASSED ===")


if __name__ == "__main__":
    main()
