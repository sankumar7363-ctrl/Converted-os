import os
import tempfile

from core.task_engine.task_engine import TaskEngine
from memory.store import MemoryStore


print("\n=== TASK ENGINE MEMORY TEST ===")


# Use an isolated temporary database.
fd, database_path = tempfile.mkstemp(
    suffix=".db"
)
os.close(fd)

try:
    memory = MemoryStore(
        database_path=database_path
    )

    # Store previous successful experience.
    memory.remember_experience(
        goal="Create a webpage",
        success=True,
        summary="Created HTML and CSS files successfully.",
    )

    print(
        "[TEST] Previous experience stored"
    )

    # Create TaskEngine using this isolated memory.
    engine = TaskEngine(
        memory=memory
    )

    task = engine.create_task(
        "Create a webpage"
    )

    workflow = engine.plan_task(
        task
    )

    assert len(workflow.steps) > 0

    assert workflow.experience_used is True

    print(
        "[TEST] Previous experience retrieved"
    )

    print(
        "[TEST] Planner used previous experience"
    )

    print(
        f"[TEST] Workflow contains "
        f"{len(workflow.steps)} steps"
    )

finally:
    if os.path.exists(database_path):
        os.remove(database_path)


print(
    "\n=== TASK ENGINE MEMORY TEST PASSED ==="
)
