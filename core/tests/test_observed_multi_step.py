from pathlib import Path

from core.ai.model import AIModel

from core.executor.observed_tool_plan_executor import (
    ObservedToolPlanExecutor,
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

from core.executor.tools.file_tools import FileTools

from core.observer.tool_observer import (
    ToolObserver,
)


class FakeFailingMultiStepAI(AIModel):

    def generate(
        self,
        prompt: str,
    ) -> str:

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
                "filename": "style.css",
                "content": "body { margin: 0; }"
            }
        }
    ]
}
"""


def main():

    print(
        "\n=== OBSERVED MULTI-STEP TEST ===\n"
    )

    workspace = (
        "workspace/observed_multi_step"
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

    ai = FakeFailingMultiStepAI()

    parser = ToolPlanParser()

    plan = parser.parse(
        ai.generate(
            "Create a website"
        )
    )

    observer = ToolObserver()

    executor = ObservedToolPlanExecutor(
        tool_system=tool_system,
        observer=observer,
    )

    observations = executor.execute(
        task_id="observed-task",
        plan=plan,
    )

    print(
        "\n[TEST] Observations:"
    )

    for observation in observations:
        print(observation)

    assert len(observations) == 2

    assert observations[0].success is True
    assert observations[0].step_index == 0

    assert observations[1].success is False
    assert observations[1].step_index == 1

    assert observations[1].tool_name == (
        "missing_tool"
    )

    expected_file = (
        Path(workspace)
        / "index.html"
    )

    assert expected_file.exists()

    style_file = (
        Path(workspace)
        / "style.css"
    )

    assert not style_file.exists()

    print(
        "\n[TEST] Step 1 succeeded"
    )

    print(
        "[TEST] Step 2 failed and was detected"
    )

    print(
        "[TEST] Step 3 was not executed"
    )

    print(
        "\n=== OBSERVED MULTI-STEP "
        "TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
