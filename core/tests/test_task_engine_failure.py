import pytest

from core.task_engine.task_engine import TaskEngine
from core.models.task import TaskStatus


class FailingToolAgent:

    def run(self, task_id: str, goal: str):
        raise RuntimeError("Simulated tool execution failure")


def test_task_engine_failure():
    engine = TaskEngine(
        tool_agent=FailingToolAgent()
    )

    task = engine.create_task(
        "Create a webpage"
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated tool execution failure",
    ):
        engine.execute_task(task)

    assert task.status == TaskStatus.FAILED

    assert task.result == (
        "Simulated tool execution failure"
    )
