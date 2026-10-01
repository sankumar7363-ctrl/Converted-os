from core.models.task import TaskStatus
from core.task_engine.task_engine import TaskEngine
from planner.workflow import WorkflowStatus


def test_task_planning():
    engine = TaskEngine()

    task = engine.create_task(
        "Create a webpage"
    )

    workflow = engine.plan_task(
        task,
        memories=[],
    )

    assert task.status == TaskStatus.PLANNING

    assert workflow.task_id == task.id

    assert workflow.status == WorkflowStatus.CREATED

    assert len(workflow.steps) > 0

    assert workflow.experience_used is False
