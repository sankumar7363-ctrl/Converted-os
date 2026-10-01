from planner.workflow import TemporaryWorkflow, WorkflowStep
from core.models.task import Task


class Planner:

    def create_workflow(
        self,
        task: Task,
        memories: list | None = None
    ) -> TemporaryWorkflow:

        steps = []
        experience_used = False

        goal = task.goal.lower()

        if "web page" in goal or "website" in goal:

            steps = [
                WorkflowStep(description="Create project folder"),
                WorkflowStep(description="Create HTML file"),
                WorkflowStep(description="Create CSS file"),
                WorkflowStep(description="Write webpage"),
                WorkflowStep(description="Start local server"),
                WorkflowStep(description="Open webpage for inspection"),
                WorkflowStep(description="Verify the result"),
            ]

            if memories:
                experience_used = True

                print(
                    "[PLANNER] Previous successful experience found"
                )

                print(
                    "[PLANNER] Workflow informed by experience"
                )

        else:

            steps = [
                WorkflowStep(
                    description=f"Analyze goal: {task.goal}"
                ),
                WorkflowStep(
                    description="Determine required actions"
                ),
                WorkflowStep(
                    description="Execute required actions"
                ),
                WorkflowStep(
                    description="Verify the result"
                ),
            ]

            if memories:
                experience_used = True

                print(
                    "[PLANNER] Previous experience found"
                )

        return TemporaryWorkflow(
            task_id=task.id,
            steps=steps,
            experience_used=experience_used,
        )

    def create_recovery_workflow(
        self,
        task: Task,
        failed_workflow: TemporaryWorkflow
    ) -> TemporaryWorkflow:

        print("[PLANNER] Previous workflow failed")
        print("[PLANNER] Creating recovery workflow")

        recovery_steps = []

        goal = task.goal.lower()

        if "web page" in goal or "website" in goal:

            recovery_steps = [
                WorkflowStep(
                    description="Create project folder"
                ),
                WorkflowStep(
                    description="Create HTML file"
                ),
                WorkflowStep(
                    description="Create CSS file"
                ),
                WorkflowStep(
                    description="Write webpage"
                ),
                WorkflowStep(
                    description="Verify webpage files"
                ),
            ]

        else:

            recovery_steps = [
                WorkflowStep(
                    description=f"Re-analyze goal: {task.goal}"
                ),
                WorkflowStep(
                    description="Determine an alternative approach"
                ),
                WorkflowStep(
                    description="Execute alternative approach"
                ),
                WorkflowStep(
                    description="Verify the result"
                ),
            ]

        print(
            "[PLANNER] Recovery workflow created"
        )

        return TemporaryWorkflow(
            task_id=task.id,
            steps=recovery_steps,
            experience_used=True,
        )
