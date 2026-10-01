from core.agent.tool_agent import ToolAgent

from core.ai.model import AIModel

from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)
from core.executor.tool_discovery import ToolDiscovery
from core.executor.tool_plan_executor import ToolPlanExecutor
from core.executor.tool_system import ToolSystem

from core.task_engine.task_engine import TaskEngine
from core.models.task import TaskStatus


class FakeAIModel(AIModel):

    def generate(
        self,
        prompt: str,
    ) -> str:

        print(
            "\n[FAKE AI] Generating tool plan"
        )

        return """
{
    "goal": "Create a file called hello.txt",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "hello.txt",
                "content": "Hello from TaskEngine!"
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


print(
    "\n=== TASK ENGINE REAL TOOL AGENT TEST ==="
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

tool_agent = ToolAgent(
    ai_model=ai_model,
    discovery=discovery,
    executor=executor,
)

engine = TaskEngine(
    tool_agent=tool_agent
)

task = engine.create_task(
    "Create a file called hello.txt"
)

results = engine.execute_task(
    task
)

assert task.status == TaskStatus.COMPLETED

assert len(results) == 1

assert results[0]["status"] == "allow"

assert results[0]["tool"] == "create_file"

assert (
    "Created hello.txt"
    in results[0]["result"]
)

print(
    "\n[TEST] TaskEngine called real ToolAgent"
)

print(
    "[TEST] AI generated executable ToolPlan"
)

print(
    "[TEST] ToolPlan executed successfully"
)

print(
    "[TEST] Result returned to TaskEngine"
)

print(
    "\n=== TASK ENGINE REAL TOOL AGENT TEST PASSED ==="
)
