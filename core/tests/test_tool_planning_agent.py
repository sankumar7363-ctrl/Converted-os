from core.agent.tool_planning_agent import (
    ToolPlanningAgent,
)

from core.executor.tool_catalog import (
    ToolCatalog,
)

from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)

from core.executor.tool_discovery import (
    ToolDiscovery,
)

from core.ai.model import AIModel


class FakeAIModel(AIModel):

    def generate(
        self,
        prompt: str,
    ) -> str:

        print(
            "\n[FAKE AI] Prompt received:"
        )

        print(prompt)

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

    return f"Created {filename}"


def main():

    print(
        "\n=== TOOL PLANNING AGENT TEST ===\n"
    )

    catalog = ToolCatalog()

    catalog.register(
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
        catalog=catalog
    )

    ai_model = FakeAIModel()

    planner = ToolPlanningAgent(
        ai_model=ai_model,
        discovery=discovery,
    )

    goal = (
        "Create a file called hello.txt"
    )

    print(
        f"[TEST] Goal: {goal}"
    )

    plan = planner.create_plan(
        goal
    )

    print(
        "\n[TEST] Generated plan:"
    )

    print(
        f"Goal: {plan.goal}"
    )

    print(
        f"Calls: {len(plan.calls)}"
    )

    for call in plan.calls:

        print(
            f"Tool: {call.tool_name}"
        )

        print(
            f"Arguments: {call.arguments}"
        )

    assert (
        plan.goal
        == goal
    )

    assert (
        len(plan.calls)
        == 1
    )

    assert (
        plan.calls[0].tool_name
        == "create_file"
    )

    assert (
        plan.calls[0].arguments[
            "filename"
        ]
        == "hello.txt"
    )

    assert (
        plan.calls[0].arguments[
            "content"
        ]
        == "Hello Converted OS!"
    )

    print(
        "\n[TEST] Tool plan generated correctly"
    )

    print(
        "\n=== TOOL PLANNING AGENT TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
