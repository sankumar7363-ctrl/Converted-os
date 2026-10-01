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
from core.models.task import TaskStatus
from core.task_engine.task_engine import TaskEngine


class FakeAutonomousAI(AIModel):

    def generate(self, prompt: str) -> str:

        if "recovery planner" in prompt.lower():

            print(
                "[FAKE AI] Generating recovery plan"
            )

            return """
{
    "goal": "Recover failed task step",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "recovered.txt",
                "content": "Recovered by TaskEngine"
            }
        }
    ]
}
"""

        return """
{
    "goal": "Create TaskEngine files",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "first.txt",
                "content": "Created first"
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
                "content": "created last"
            }
        }
    ]
}
"""


def main():

    print(
        "\n=== TASK ENGINE AUTONOMOUS RECOVERY TEST ===\n"
    )

    workspace = (
        "workspace/task_engine_autonomous_recovery"
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

    ai_model = FakeAutonomousAI()

    autonomous_agent = AutonomousToolAgent(
        ai_model=ai_model,
        discovery=discovery,
        tool_system=tool_system,
    )

    engine = TaskEngine(
        autonomous_agent=autonomous_agent
    )

    task = engine.create_task(
        "Create TaskEngine files"
    )

    results = engine.execute_task(
        task
    )

    print(
        "\n[TEST] Final task status:",
        task.status,
    )

    print(
        "[TEST] Final results:"
    )

    for result in results:
        print(result)

    first_file = (
        Path(workspace)
        / "first.txt"
    )

    recovered_file = (
        Path(workspace)
        / "recovered.txt"
    )

    assert first_file.exists()
    assert recovered_file.exists()

    assert (
        first_file.read_text(
            encoding="utf-8"
        )
        == "Created first"
    )

    assert (
        recovered_file.read_text(
            encoding="utf-8"
        )
        == "Recovered by TaskEngine"
    )

    assert (
        task.status
        == TaskStatus.COMPLETED
    )

    assert (
        task.result
        == "Task execution completed successfully."
    )

    assert len(results) == 4

    print(
        "\n[TEST] TaskEngine created the task"
    )

    print(
        "[TEST] Autonomous agent executed the plan"
    )

    print(
        "[TEST] Failed step triggered recovery"
    )

    print(
        "[TEST] Recovery created the expected file"
    )

    print(
        "[TEST] TaskEngine marked the task COMPLETED"
    )

    print(
        "\n=== TASK ENGINE AUTONOMOUS "
        "RECOVERY TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
