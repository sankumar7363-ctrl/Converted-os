from core.agent.tool_agent import ToolAgent

from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)
from core.executor.tool_discovery import ToolDiscovery
from core.executor.tool_plan_executor import ToolPlanExecutor
from core.executor.tool_system import ToolSystem

from core.ai.model import AIModel


class FakeAIModel(AIModel):

    def generate(
        self,
        prompt: str,
    ) -> str:

        print("\n[FAKE AI] Generating tool plan")

        return """
{
    "goal": "Create a file called hello.txt",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "hello.txt",
                "content": "Hello Converted OS!"
            }
        }
    ]
}
"""


def create_file(
    filename: str,
    content: str,
) -> str:

    print(
        f"[REAL TOOL] Creating file: {filename}"
    )

    return (
        f"Created {filename} "
        f"with content: {content}"
    )


def main():

    print(
        "\n=== END-TO-END TOOL AGENT TEST ===\n"
    )

    tool_system = ToolSystem()

    tool_system.register(
        definition=ToolDefinition(
            name="create_file",
            description="Create a file",
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
        implementation=create_file,
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

    task_id = "end-to-end-task"

    goal = (
        "Create a file called hello.txt"
    )

    results = agent.run(
        task_id=task_id,
        goal=goal,
    )

    print(
        "\n[TEST] Final results:"
    )

    print(results)

    assert len(results) == 1

    assert (
        results[0]["status"]
        == "allow"
    )

    assert (
        results[0]["tool"]
        == "create_file"
    )

    assert (
        "Created hello.txt"
        in results[0]["result"]
    )

    print(
        "\n[TEST] AI → ToolPlan → Execution "
        "worked successfully"
    )

    print(
        "\n=== END-TO-END TOOL AGENT TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
