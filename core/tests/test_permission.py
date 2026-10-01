from core.models.task import Task
from core.executor.executor import Executor
from planner.workflow import (
    TemporaryWorkflow,
    WorkflowStep,
    WorkflowStatus,
)


def main():

    print("\n=== TASK-AWARE PERMISSION TEST ===\n")

    executor = Executor()

    # Create a test task
    task = Task(
        goal="Prepare a development environment"
    )

    # Create a workflow with:
    # 1. Low-risk action
    # 2. Medium-risk action requiring permission
    # 3. Another low-risk action
    workflow = TemporaryWorkflow(
        task_id=task.id,
        steps=[
            WorkflowStep(
                description="Create project folder"
            ),
            WorkflowStep(
                description="Install Python package"
            ),
            WorkflowStep(
                description="Create HTML file"
            ),
        ],
    )

    print(f"[TEST] Task ID: {task.id}")

    # Execute until permission is required
    result = executor.execute(workflow)

    print(
        f"\n[TEST] Workflow status: "
        f"{result.status.value}"
    )

    print(
        f"[TEST] Permission pending: "
        f"{task.id in executor.permissions.pending_actions}"
    )

    # Verify the workflow paused correctly
    assert result.status == WorkflowStatus.PENDING

    assert (
        task.id in executor.paused_workflows
    )

    assert (
        task.id in executor.paused_step_indexes
    )

    assert (
        task.id in executor.permissions.pending_actions
    )

    print(
        "[TEST] Workflow correctly paused "
        "for permission"
    )

    # Approve the task
    print("\n[TEST] Approving task...")

    result = executor.approve_pending(
        task.id
    )

    assert result is not None

    print(
        f"[TEST] Final status: "
        f"{result.status.value}"
    )

    # Verify completion
    assert (
        result.status
        == WorkflowStatus.COMPLETED
    )

    assert all(
        step.completed
        for step in result.steps
    )

    assert (
        task.id not in executor.paused_workflows
    )

    assert (
        task.id
        not in executor.paused_step_indexes
    )

    assert (
        not executor.permissions.is_pending(
            task.id
        )
    )

    print(
        "[TEST] All workflow steps completed"
    )

    print(
        "\n=== TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
