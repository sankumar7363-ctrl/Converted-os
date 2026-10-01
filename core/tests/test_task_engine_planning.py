from core.models.task import TaskStatus
from core.task_engine.task_engine import TaskEngine
from planner.workflow import WorkflowStatus


print("\n=== TASK ENGINE PLANNING TEST ===")

engine = TaskEngine()

task = engine.create_task(
    "Create a webpage"
)

workflow = engine.plan_task(task)

assert task.status == TaskStatus.PLANNING

assert workflow.task_id == task.id

assert workflow.status == WorkflowStatus.CREATED

assert len(workflow.steps) > 0

assert workflow.experience_used is False

print("[TEST] Task moved to planning")

print(
    f"[TEST] Workflow created with "
    f"{len(workflow.steps)} steps"
)

print("[TEST] Workflow linked to task")

print("\n[TEST] Workflow steps:")

for index, step in enumerate(workflow.steps, start=1):
    print(f"  {index}. {step.description}")

print("\n=== TASK ENGINE PLANNING TEST PASSED ===")
