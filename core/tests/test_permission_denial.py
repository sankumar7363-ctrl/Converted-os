from core.models.task import Task
from core.executor.executor import Executor
from planner.workflow import (
    TemporaryWorkflow,
    WorkflowStep,
    WorkflowStatus,
)


def main():

    print("\n=== TASK-AWARE DENIAL TEST ===\n")

    executor = Executor()

    task = Task(
        goal="Prepare a development environment"
    )

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

    # Run until permission is required.
    result = executor.execute(workflow)

    print(
        f"\n[TEST] Workflow status: "
        f"{result.status.value}"
    )

    assert result.status == WorkflowStatus.PENDING

    assert (
        task.id in executor.paused_workflows
    )

    assert (
        executor.permissions.is_pending(
            task.id
        )
    )

    print(
        "[TEST] Workflow correctly paused"
    )

    # Deny permission.
    print("\n[TEST] Denying task...")

    result = executor.deny_pending(
        task.id
    )

    assert result is not None

    print(
        f"[TEST] Final status: "
        f"{result.status.value}"
    )

    assert (
        result.status
        == WorkflowStatus.FAILED
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

    # The permission-required step must NOT execute.
    assert (
        result.steps[1].completed
        is False
    )

    print(
        "[TEST] Workflow stopped correctly"
    )

    print(
        "[TEST] Permission request removed"
    )

    print(
        "\n=== DENIAL TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
