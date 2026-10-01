from pathlib import Path

from core.ai.model import AIModel

from core.agent.recovery_tool_agent import (
    RecoveryToolAgent,
)

from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)

from core.executor.tool_discovery import (
    ToolDiscovery,
)

from core.executor.tool_plan_executor import (
    ToolPlanExecutor,
)

from core.executor.tool_system import (
    ToolSystem,
)

from core.executor.tools.file_tools import (
    FileTools,
)

from core.observer.file_observer import (
    FileObserver,
)


class RecoveryFakeAI(AIModel):

    def __init__(self):

        self.calls = 0

    def generate(
        self,
        prompt: str,
    ) -> str:

        self.calls += 1

        print(
            f"\n[FAKE AI] Planning attempt "
            f"{self.calls}"
        )

        if self.calls == 1:

            return """
{
    "goal": "Create recovery.txt",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "recovery.txt",
                "content": "WRONG CONTENT"
            }
        }
    ]
}
"""

        return """
{
    "goal": "Recover and create recovery.txt correctly",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "recovery.txt",
                "content": "Recovery succeeded!"
            }
        }
    ]
}
"""


def main():

    print(
        "\n=== RECOVERY TOOL AGENT TEST ===\n"
    )

    workspace = (
        "workspace/recovery_test"
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

    observer = FileObserver()

    ai_model = RecoveryFakeAI()

    agent = RecoveryToolAgent(
        ai_model=ai_model,
        discovery=discovery,
        executor=executor,
        observer=observer,
    )

    goal = (
        "Create recovery.txt"
    )

    expected_file = str(
        Path(workspace)
        / "recovery.txt"
    )

    expected_content = (
        "Recovery succeeded!"
    )

    result = agent.run(
        task_id="recovery-task",
        goal=goal,
        expected_file=expected_file,
        expected_content=expected_content,
    )

    print(
        "\n[TEST] Final result:"
    )

    print(result)

    assert result["success"] is True
    assert result["verified"] is True
    assert result["attempts"] == 2

    actual_content = Path(
        expected_file
    ).read_text(
        encoding="utf-8"
    )

    assert (
        actual_content
        == expected_content
    )

    print(
        "\n[TEST] First attempt failed"
    )

    print(
        "[TEST] Recovery plan succeeded"
    )

    print(
        "[TEST] Final result was verified"
    )

    print(
        "\n=== RECOVERY TOOL AGENT "
        "TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
