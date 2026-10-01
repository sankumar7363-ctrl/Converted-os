from core.task_engine.task_engine import TaskEngine
from core.models.task import TaskStatus


class FailingToolAgent:

    def run(self, task_id: str, goal: str):
        print("[FAKE TOOL AGENT] Simulating execution failure")
        raise RuntimeError("Simulated tool execution failure")


print("\n=== TASK ENGINE FAILURE TEST ===")

engine = TaskEngine(
    tool_agent=FailingToolAgent()
)

task = engine.create_task(
    "Create a webpage"
)

try:
    engine.execute_task(task)
except RuntimeError as error:
    print(
        f"[TEST] Caught expected error: {error}"
    )

assert task.status == TaskStatus.FAILED

assert task.result == (
    "Simulated tool execution failure"
)

print("[TEST] Task moved to FAILED")
print("[TEST] Failure reason stored")

print("\n=== TASK ENGINE FAILURE TEST PASSED ===")
