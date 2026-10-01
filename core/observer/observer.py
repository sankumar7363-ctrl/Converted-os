from pathlib import Path
from planner.workflow import TemporaryWorkflow


class Observer:

    def check_file_exists(self, filepath: str) -> bool:
        return Path(filepath).exists()

    def verify_workflow(self, workflow: TemporaryWorkflow) -> bool:

        if workflow.status == "failed":
            print("[OBSERVER] Workflow failure detected")
            return False

        for step in workflow.steps:

            if not step.completed:
                print(
                    f"[OBSERVER] Incomplete step: "
                    f"{step.description}"
                )

                return False

        print("[OBSERVER] Workflow verified successfully")

        return True
