from core.models.task import TaskStatus
from core.task_engine.task_engine import TaskEngine


def test_task_creation_and_status_flow():
    engine = TaskEngine()

    task = engine.create_task("Create a webpage")

    assert task.goal == "Create a webpage"
    assert task.status == TaskStatus.CREATED

    engine.set_status(task, TaskStatus.PLANNING)
    assert task.status == TaskStatus.PLANNING

    engine.set_status(task, TaskStatus.EXECUTING)
    assert task.status == TaskStatus.EXECUTING

    engine.set_status(task, TaskStatus.VERIFYING)
    assert task.status == TaskStatus.VERIFYING

    engine.complete_task(
        task,
        result="Webpage created successfully",
    )

    assert task.status == TaskStatus.COMPLETED
    assert task.result == "Webpage created successfully"


def test_task_failure():
    engine = TaskEngine()

    failed_task = engine.create_task("Run a failing task")

    engine.set_status(
        failed_task,
        TaskStatus.EXECUTING,
    )

    engine.fail_task(
        failed_task,
        error="Test failure",
    )

    assert failed_task.status == TaskStatus.FAILED
    assert failed_task.result == "Test failure"
