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
import os
import tempfile

from memory.store import MemoryStore



class FakeAutonomousAI(AIModel):

    def generate(self, prompt: str) -> str:

        if "recovery planner" in prompt.lower():
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


def test_task_engine_autonomous_recovery(tmp_path):
    workspace = tmp_path / "task_engine_autonomous_recovery"

    file_tools = FileTools(
        workspace=str(workspace)
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

    first_file = workspace / "first.txt"
    recovered_file = workspace / "recovered.txt"

    assert first_file.exists()
    assert recovered_file.exists()

    assert first_file.read_text(
        encoding="utf-8"
    ) == "Created first"

    assert recovered_file.read_text(
        encoding="utf-8"
    ) == "Recovered by TaskEngine"

    assert task.status == TaskStatus.COMPLETED

    assert task.result == (
        "Task execution completed successfully."
    )

    assert len(results) == 4


def test_task_engine_passes_experience_to_ai_planner(tmp_path):

    workspace = tmp_path / "task_engine_experience"

    file_tools = FileTools(
        workspace=str(workspace)
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

    class ExperienceAwareAI(AIModel):

        def __init__(self):
            self.planning_prompt = ""

        def generate(self, prompt: str) -> str:

            if "Previous experiences" in prompt:

                self.planning_prompt = prompt

                return """
{
    "goal": "Create an improved webpage",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "improved.txt",
                "content": "Improved using previous experience"
            }
        }
    ]
}
"""

            return """
{
    "goal": "Create an improved webpage",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "improved.txt",
                "content": "Improved using previous experience"
            }
        }
    ]
}
"""

    ai_model = ExperienceAwareAI()

    autonomous_agent = AutonomousToolAgent(
        ai_model=ai_model,
        discovery=discovery,
        tool_system=tool_system,
    )

    fd, database_path = tempfile.mkstemp(
        suffix=".db"
    )
    os.close(fd)

    try:

        memory = MemoryStore(
            database_path=database_path
        )

        memory.remember_experience(
            goal="Create a webpage",
            success=True,
            summary=(
                "Created HTML and CSS successfully "
                "after using a simpler workflow."
            ),
        )

        engine = TaskEngine(
            memory=memory,
            autonomous_agent=autonomous_agent,
        )

        task = engine.create_task(
            "Create a webpage"
        )

        results = engine.execute_task(
            task
        )

        assert task.status == TaskStatus.COMPLETED

        assert len(results) > 0

        assert (
            "Previous experiences"
            in ai_model.planning_prompt
        )

        assert (
            "Created HTML and CSS successfully"
            in ai_model.planning_prompt
        )

        improved_file = (
            workspace / "improved.txt"
        )

        assert improved_file.exists()

    finally:

        if os.path.exists(database_path):
            os.remove(database_path)
