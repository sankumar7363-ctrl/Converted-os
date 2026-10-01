from core.models.task import Task, TaskStatus
from core.planner.planner import Planner
from memory.store import MemoryStore
from core.learning.learning_engine import LearningEngine
from core.agent.tool_agent import ToolAgent
from core.agent.autonomous_tool_agent import AutonomousToolAgent
from planner.workflow import TemporaryWorkflow


class TaskEngine:
    def __init__(
        self,
        planner: Planner | None = None,
        memory: MemoryStore | None = None,
        learning_engine: LearningEngine | None = None,
        tool_agent: ToolAgent | None = None,
        autonomous_agent: AutonomousToolAgent | None = None,
    ):
        self.planner = planner if planner is not None else Planner()
        self.memory = memory if memory is not None else MemoryStore()

        self.learning_engine = (
            learning_engine
            if learning_engine is not None
            else LearningEngine(memory=self.memory)
        )

        self.tool_agent = tool_agent
        self.autonomous_agent = autonomous_agent

    def create_task(self, goal: str) -> Task:
        if not goal or not goal.strip():
            raise ValueError("Task goal cannot be empty")

        task = Task(goal=goal.strip())

        print(f"[TASK ENGINE] Task created: {task.id}")
        print(f"[TASK ENGINE] Goal: {task.goal}")
        print(f"[TASK ENGINE] Status: {task.status.value}")

        return task

    def set_status(self, task: Task, status: TaskStatus) -> Task:
        task.status = status
        print(f"[TASK ENGINE] {task.id} → {task.status.value}")
        return task

    def plan_task(
        self,
        task: Task,
        memories: list | None = None,
    ) -> TemporaryWorkflow:
        self.set_status(task, TaskStatus.PLANNING)

        print(f"[TASK ENGINE] Planning task: {task.id}")

        if memories is None:
            print("[TASK ENGINE] Searching memory...")
            memories = self.learning_engine.find_relevant_experiences(
                goal=task.goal
            )

        print(f"[TASK ENGINE] Relevant memories: {len(memories)}")

        workflow = self.planner.create_workflow(
            task=task,
            memories=memories,
        )

        print(f"[TASK ENGINE] Workflow created: {workflow.id}")
        print(f"[TASK ENGINE] Workflow steps: {len(workflow.steps)}")
        print(f"[TASK ENGINE] Experience used: {workflow.experience_used}")

        return workflow

    def execution_succeeded(self, results: list) -> bool:
        if not results:
            return False

        final_results = {}

        for index, result in enumerate(results):
            if isinstance(result, dict):
                step_index = result.get("step_index", index)

                if "success" in result:
                    success = result["success"]
                elif result.get("status") == "success":
                    success = True
                elif (
                    result.get("status") == "allow"
                    and result.get("result") is not None
                ):
                    success = True
                else:
                    success = False

            else:
                step_index = getattr(result, "step_index", index)
                success = getattr(result, "success", False)

            final_results[step_index] = success

        return all(final_results.values())

    def execute_task(self, task: Task):
        if self.tool_agent is None and self.autonomous_agent is None:
            raise RuntimeError("No execution agent is configured")

        self.set_status(task, TaskStatus.EXECUTING)

        print(f"[TASK ENGINE] Executing task: {task.id}")

        try:
            if self.autonomous_agent is not None:
                print("[TASK ENGINE] Using autonomous recovery agent")

                results = self.autonomous_agent.run(
                    task_id=task.id,
                    goal=task.goal,
                )
            else:
                results = self.tool_agent.run(
                    task_id=task.id,
                    goal=task.goal,
                )

        except Exception as error:
            self.fail_task(task, error=str(error))
            raise

        print(f"[TASK ENGINE] Execution returned {len(results)} result(s)")

        success = self.execution_succeeded(results)

        experience = self.learning_engine.create_experience(
            goal=task.goal,
            results=results,
        )

        self.learning_engine.store_experience(experience)

        print(
            f"[TASK ENGINE] Experience stored: "
            f"{experience.outcome.value}"
        )

        if success:
            self.complete_task(
                task,
                result="Task execution completed successfully.",
            )
        else:
            self.fail_task(
                task,
                error="Task execution finished with an unresolved failure.",
            )

        return results

    def complete_task(
        self,
        task: Task,
        result: str | None = None,
    ) -> Task:
        task.status = TaskStatus.COMPLETED
        task.result = result

        print(f"[TASK ENGINE] Task completed: {task.id}")

        if result:
            print(f"[TASK ENGINE] Result: {result}")

        return task

    def fail_task(
        self,
        task: Task,
        error: str | None = None,
    ) -> Task:
        task.status = TaskStatus.FAILED
        task.result = error

        print(f"[TASK ENGINE] Task failed: {task.id}")

        if error:
            print(f"[TASK ENGINE] Error: {error}")

        return task
