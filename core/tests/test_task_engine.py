from core.models.task import TaskStatus
from core.task_engine.task_engine import TaskEngine


print("\n=== TASK ENGINE TEST ===")

engine = TaskEngine()


# 1. Create task
task = engine.create_task("Create a webpage")

assert task.goal == "Create a webpage"
assert task.status == TaskStatus.CREATED

print("[TEST] Task creation verified")


# 2. Move to planning
engine.set_status(task, TaskStatus.PLANNING)

assert task.status == TaskStatus.PLANNING

print("[TEST] Planning status verified")


# 3. Move to executing
engine.set_status(task, TaskStatus.EXECUTING)

assert task.status == TaskStatus.EXECUTING

print("[TEST] Executing status verified")


# 4. Move to verifying
engine.set_status(task, TaskStatus.VERIFYING)

assert task.status == TaskStatus.VERIFYING

print("[TEST] Verifying status verified")


# 5. Complete task
engine.complete_task(
    task,
    result="Webpage created successfully"
)

assert task.status == TaskStatus.COMPLETED
assert task.result == "Webpage created successfully"

print("[TEST] Task completion verified")


# 6. Test failure path separately
failed_task = engine.create_task("Run a failing task")

engine.set_status(
    failed_task,
    TaskStatus.EXECUTING
)

engine.fail_task(
    failed_task,
    error="Test failure"
)

assert failed_task.status == TaskStatus.FAILED
assert failed_task.result == "Test failure"

print("[TEST] Task failure verified")


print("\n=== TASK ENGINE TEST PASSED ===")
