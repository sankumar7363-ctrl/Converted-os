from core.task_engine.task_engine import TaskEngine
from core.models.task import TaskStatus


class FakeToolAgent:

    def __init__(self):
        self.calls = []

    def run(self, task_id: str, goal: str):
        self.calls.append(
            {
                "task_id": task_id,
                "goal": goal,
            }
        )

        return [
            {
                "status": "success",
                "message": "Fake execution completed",
            }
        ]


def test_task_engine_execution():
    tool_agent = FakeToolAgent()

    engine = TaskEngine(
        tool_agent=tool_agent
    )

    task = engine.create_task(
        "Create a webpage"
    )

    results = engine.execute_task(
        task
    )

    assert task.status == TaskStatus.COMPLETED

    assert task.result == (
        "Task execution completed successfully."
    )

    assert len(results) == 1

    assert len(tool_agent.calls) == 1

    assert tool_agent.calls[0]["task_id"] == task.id

    assert tool_agent.calls[0]["goal"] == "Create a webpage"
