from core.models.task import Task
from core.models.outcome import (
    TaskOutcome,
    OutcomeStatus,
)

from core.planner.planner import Planner
from core.planner.ai_planner import AIPlanner

from core.executor.executor import Executor
from core.observer.observer import Observer

from memory.store import MemoryStore

from config.ai_config import AIConfig
from core.ai.health import AIHealthChecker
from core.ai.status import AIAvailability


class Agent:

    def __init__(self):

        # AI configuration
        self.ai_config = AIConfig.from_environment()

        # Check AI availability
        health_checker = AIHealthChecker()

        self.ai_status = health_checker.check(
            self.ai_config
        )

        self.ai_model = self.ai_status.model

        if self.ai_status.status == (
            AIAvailability.AVAILABLE
        ):

            print(
                "[AGENT] AI provider available"
            )

            self.ai_planner = AIPlanner(
                self.ai_model
            )

        else:

            self.ai_planner = None

            print(
                "[AGENT] AI provider unavailable"
            )

            print(
                f"[AGENT] Status: "
                f"{self.ai_status.status.value}"
            )

            print(
                f"[AGENT] Reason: "
                f"{self.ai_status.message}"
            )

        # Rule-based planner kept for recovery
        self.recovery_planner = Planner()

        # Execution and observation
        self.executor = Executor()
        self.observer = Observer()

        # Persistent memory
        self.memory = MemoryStore()

        # Tasks currently waiting for permission
        self.pending_tasks = {}

    def run(
        self,
        goal: str,
        simulate_failure: bool = False
    ):

        # 1. Create task
        task = Task(goal=goal)

        print(
            f"\n[AGENT] Goal: {task.goal}"
        )

        # AI is currently required for
        # workflow generation.
        if self.ai_planner is None:

            print(
                "[AGENT] Cannot execute task"
            )

            print(
                "[AGENT] AI planner unavailable"
            )

            return TaskOutcome(
                task_id=task.id,
                success=False,
                status=OutcomeStatus.BLOCKED,
                summary=(
                    "Task could not start because "
                    "the AI planner is unavailable"
                ),
            )

        # 2. Retrieve relevant memories
        memories = self.memory.search(
            task.goal
        )

        print(
            f"[AGENT] Memories found: "
            f"{len(memories)}"
        )

        for memory in memories:

            print(
                f"[MEMORY] "
                f"{memory['content']}"
            )

        # 3. Generate AI workflow
        workflow = self.ai_planner.generate_workflow(
            task,
            memories
        )

        print(
            f"[AGENT] AI workflow created: "
            f"{len(workflow.steps)} steps"
        )

        # 4. Execute AI-generated workflow
        workflow = self.executor.execute(
            workflow,
            simulate_failure=simulate_failure
        )

        # 5. Permission checkpoint
        if workflow.status.value == "pending":

            print(
                "[AGENT] Workflow is waiting "
                "for user permission"
            )

            self.pending_tasks[task.id] = task

            return TaskOutcome(
                task_id=task.id,
                success=False,
                status=OutcomeStatus.WAITING,
                summary=(
                    "Task is waiting for user permission"
                ),
            )

        # 6. Observe / verify
        success = self.observer.verify_workflow(
            workflow
        )

        # 7. Recovery attempt
        if not success:

            print(
                "[AGENT] Initial AI workflow failed"
            )

            print(
                "[AGENT] Starting recovery"
            )

            recovery_workflow = (
                self.recovery_planner.create_recovery_workflow(
                    task,
                    workflow
                )
            )

            print(
                f"[AGENT] Recovery workflow created: "
                f"{len(recovery_workflow.steps)} steps"
            )

            recovery_workflow = (
                self.executor.execute(
                    recovery_workflow,
                    simulate_failure=False
                )
            )

            success = (
                self.observer.verify_workflow(
                    recovery_workflow
                )
            )

            del recovery_workflow

            print(
                "[AGENT] Recovery workflow discarded"
            )

        # 8. Create final outcome
        outcome_status = (
            OutcomeStatus.COMPLETED
            if success
            else OutcomeStatus.FAILED
        )

        outcome = TaskOutcome(
            task_id=task.id,
            success=success,
            status=outcome_status,
            summary=(
                "Task completed successfully"
                if success
                else "Task failed after recovery attempt"
            ),
        )

        print(
            f"[AGENT] Success: "
            f"{outcome.success}"
        )

        # 9. Store experience
        self.memory.remember_experience(
            goal=task.goal,
            success=outcome.success,
            status=outcome.status.value,
            summary=outcome.summary
        )

        print(
            "[AGENT] Learning stored"
        )

        # 10. Discard initial workflow
        del workflow

        print(
            "[AGENT] Temporary workflow discarded"
        )

        return outcome

    def approve_pending(
        self,
        task_id: str,
    ):

        if task_id not in self.pending_tasks:

            print(
                "[AGENT] No pending task found: "
                f"{task_id}"
            )

            return None

        task = self.pending_tasks[task_id]

        print(
            f"\n[AGENT] Approving pending task: "
            f"{task.goal}"
        )

        workflow = self.executor.approve_pending()

        if workflow is None:

            print(
                "[AGENT] Could not resume task"
            )

            return None

        success = self.observer.verify_workflow(
            workflow
        )

        outcome_status = (
            OutcomeStatus.COMPLETED
            if success
            else OutcomeStatus.FAILED
        )

        outcome = TaskOutcome(
            task_id=task.id,
            success=success,
            status=outcome_status,
            summary=(
                "Task completed successfully"
                if success
                else "Task failed after permission approval"
            ),
        )

        self.memory.remember_experience(
            goal=task.goal,
            success=outcome.success,
            status=outcome.status.value,
            summary=outcome.summary
        )

        del self.pending_tasks[task_id]

        print(
            "[AGENT] Pending task completed"
        )

        return outcome

    def deny_pending(
        self,
        task_id: str,
    ):

        if task_id not in self.pending_tasks:

            print(
                "[AGENT] No pending task found: "
                f"{task_id}"
            )

            return None

        task = self.pending_tasks[task_id]

        print(
            f"\n[AGENT] Denying pending task: "
            f"{task.goal}"
        )

        workflow = self.executor.deny_pending()

        if workflow is None:

            print(
                "[AGENT] Could not deny task"
            )

            return None

        outcome = TaskOutcome(
            task_id=task.id,
            success=False,
            status=OutcomeStatus.FAILED,
            summary=(
                "Task stopped because "
                "user denied permission"
            ),
        )

        self.memory.remember_experience(
            goal=task.goal,
            success=False,
            status=outcome.status.value,
            summary=outcome.summary
        )

        del self.pending_tasks[task_id]

        print(
            "[AGENT] Pending task denied"
        )

        return outcome
