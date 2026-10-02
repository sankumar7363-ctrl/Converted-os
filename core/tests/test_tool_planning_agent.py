from core.agent.tool_planning_agent import ToolPlanningAgent
from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)
from core.executor.tool_discovery import ToolDiscovery
from core.ai.model import AIModel


class FakeAIModel(AIModel):

    def generate(
        self,
        prompt: str,
    ) -> str:

        assert "Previous experiences" in prompt
        assert "previous approach failed" in prompt

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

def test_tool_planning_agent_uses_experience():

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

    goal = "Create a file called hello.txt"

    memories = [
        {
            "content": (
                "Previous approach failed because "
                "the previous approach failed."
            )
        }
    ]

    plan = planner.create_plan(
        goal=goal,
        memories=memories,
    )

    assert plan.goal == goal
    assert len(plan.calls) == 1
    assert plan.calls[0].tool_name == "create_file"

    assert (
        plan.calls[0].arguments["filename"]
        == "hello.txt"
    )

    assert (
        plan.calls[0].arguments["content"]
        == "Hello Converted OS!"
    )


def test_tool_planning_agent_without_experience():

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

    class NoMemoryAI(AIModel):

        def generate(self, prompt: str) -> str:

            assert "Previous experiences" not in prompt

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

    planner = ToolPlanningAgent(
        ai_model=NoMemoryAI(),
        discovery=discovery,
    )

    plan = planner.create_plan(
        goal="Create a file called hello.txt"
    )

    assert plan.goal == "Create a file called hello.txt"
    assert len(plan.calls) == 1
    assert plan.calls[0].tool_name == "create_file"
