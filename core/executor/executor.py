from planner.workflow import (
    TemporaryWorkflow,
    WorkflowStatus,
)

from tools.file_tool import FileTool

from core.policy.classifier import ActionClassifier
from core.policy.permission import PermissionManager
from core.policy.policy import (
    PolicyDecision,
    PolicyEngine,
)


class Executor:

    def __init__(self):

        self.file_tool = FileTool()

        self.classifier = ActionClassifier()
        self.policy = PolicyEngine()
        self.permissions = PermissionManager()

        # Pending workflows are tracked by task ID.
        # This allows multiple tasks to wait for
        # permission independently.
        self.paused_workflows: dict[
            str,
            TemporaryWorkflow,
        ] = {}

        self.paused_step_indexes: dict[
            str,
            int,
        ] = {}

    def _check_policy(
        self,
        name: str,
        description: str,
    ):

        action = self.classifier.classify(
            name=name,
            description=description,
        )

        result = self.policy.evaluate(action)

        print(
            f"[POLICY] {name} → "
            f"risk={action.risk.value} → "
            f"decision={result.decision.value}"
        )

        return action, result

    def _execute_step(
        self,
        step,
    ):

        if step.description == "Create project folder":

            self.file_tool.create_file(
                "project/.gitkeep"
            )

        elif step.description == "Create HTML file":

            self.file_tool.create_file(
                "project/index.html",
                """<!DOCTYPE html>
<html>
<head>
    <title>Converted OS</title>
</head>
<body>
    <h1>Hello from Converted OS!</h1>
</body>
</html>
""",
            )

        elif step.description == "Create CSS file":

            self.file_tool.create_file(
                "project/style.css",
                "body { font-family: sans-serif; }\n",
            )

        step.completed = True

    def execute(
        self,
        workflow: TemporaryWorkflow,
        simulate_failure: bool = False,
    ) -> TemporaryWorkflow:

        workflow.status = WorkflowStatus.RUNNING

        for index, step in enumerate(workflow.steps):

            if step.completed:
                continue

            print(
                f"[EXECUTOR] Executing: "
                f"{step.description}"
            )

            # Testing-only failure simulation.
            if simulate_failure and index == 1:

                print(
                    f"[EXECUTOR] FAILED: "
                    f"{step.description}"
                )

                workflow.status = WorkflowStatus.FAILED

                return workflow

            action, policy_result = self._check_policy(
                name=step.description,
                description=step.description,
            )

            # High-risk action.
            if (
                policy_result.decision
                == PolicyDecision.BLOCK
            ):

                print(
                    "[EXECUTOR] Action blocked by policy"
                )

                workflow.status = WorkflowStatus.FAILED

                return workflow

            # Medium-risk action.
            if (
                policy_result.decision
                == PolicyDecision.ASK
            ):

                permission = (
                    self.permissions.request(
                        task_id=workflow.task_id,
                        action=action,
                    )
                )

                print(
                    "[EXECUTOR] Permission status: "
                    f"{permission.value}"
                )

                # Store this workflow using its task ID.
                self.paused_workflows[
                    workflow.task_id
                ] = workflow

                self.paused_step_indexes[
                    workflow.task_id
                ] = index

                workflow.status = (
                    WorkflowStatus.PENDING
                )

                return workflow

            # Low-risk action.
            self._execute_step(step)

        workflow.status = WorkflowStatus.COMPLETED

        # Remove any old pending state for this task.
        self.paused_workflows.pop(
            workflow.task_id,
            None,
        )

        self.paused_step_indexes.pop(
            workflow.task_id,
            None,
        )

        return workflow

    def approve_pending(
        self,
        task_id: str,
    ) -> TemporaryWorkflow | None:

        if task_id not in self.paused_workflows:

            print(
                "[EXECUTOR] No pending workflow "
                f"found: {task_id}"
            )

            return None

        if task_id not in self.paused_step_indexes:

            print(
                "[EXECUTOR] No pending step "
                f"found: {task_id}"
            )

            return None

        workflow = self.paused_workflows[
            task_id
        ]

        step_index = self.paused_step_indexes[
            task_id
        ]

        if not self.permissions.approve(
            task_id
        ):

            print(
                "[EXECUTOR] Permission approval failed"
            )

            return None

        print(
            "[EXECUTOR] Permission approved"
        )

        step = workflow.steps[step_index]

        self._execute_step(step)

        # Remove the pending state before resuming.
        del self.paused_workflows[task_id]

        del self.paused_step_indexes[task_id]

        # Continue executing the remaining workflow.
        return self.execute(workflow)

    def deny_pending(
        self,
        task_id: str,
    ) -> TemporaryWorkflow | None:

        if task_id not in self.paused_workflows:

            print(
                "[EXECUTOR] No pending workflow "
                f"found: {task_id}"
            )

            return None

        if task_id not in self.paused_step_indexes:

            print(
                "[EXECUTOR] No pending step "
                f"found: {task_id}"
            )

            return None

        workflow = self.paused_workflows[
            task_id
        ]

        if not self.permissions.deny(
            task_id
        ):

            print(
                "[EXECUTOR] Permission denial failed"
            )

            return None

        print(
            "[EXECUTOR] Permission denied"
        )

        workflow.status = WorkflowStatus.FAILED

        # Remove pending state.
        del self.paused_workflows[task_id]

        del self.paused_step_indexes[task_id]

        return workflow
