import os
import tempfile

from core.task_engine.task_engine import TaskEngine
from memory.store import MemoryStore


def test_task_engine_uses_previous_memory():
    fd, database_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        memory = MemoryStore(database_path=database_path)

        memory.remember_experience(
            goal="Create a webpage",
            success=True,
            summary="Created HTML and CSS files successfully.",
        )

        engine = TaskEngine(memory=memory)

        task = engine.create_task("Create a webpage")

        workflow = engine.plan_task(task)

        assert len(workflow.steps) > 0
        assert workflow.experience_used is True

    finally:
        if os.path.exists(database_path):
            os.remove(database_path)
