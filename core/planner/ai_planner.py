import json

from planner.workflow import TemporaryWorkflow, WorkflowStep
from core.models.task import Task
from core.models.ai_plan import AIPlan
from core.ai.model import AIModel


class AIPlanner:

    def __init__(self, model: AIModel):
        self.model = model

    def generate_workflow(
        self,
        task: Task,
        memories: list | None = None
    ) -> TemporaryWorkflow:

        print("[AI PLANNER] Understanding goal...")
        print(f"[AI PLANNER] Goal: {task.goal}")

        memory_context = ""

        if memories:

            print(
                f"[AI PLANNER] Retrieved "
                f"{len(memories)} relevant memories"
            )

            memory_context = "\nPrevious experience:\n"

            for memory in memories:
                memory_context += (
                    f"- {memory['content']}\n"
                )

        prompt = f"""
You are the planning intelligence of Converted OS.

User goal:
{task.goal}

{memory_context}

Determine the logical steps required to achieve the goal.

Return ONLY valid JSON in this format:

{{
    "goal": "the user's goal",
    "steps": [
        {{
            "description": "step description",
            "reason": "why this step is needed"
        }}
    ]
}}
"""

        response = self.model.generate(prompt)

        print("[AI PLANNER] Model response:")
        print(response)

        try:

            data = json.loads(response)

            plan = AIPlan.model_validate(data)

        except (json.JSONDecodeError, ValueError) as error:

            print(
                "[AI PLANNER] Invalid AI plan:"
            )
            print(error)

            raise ValueError(
                "AI model returned an invalid plan"
            ) from error

        steps = []

        for plan_step in plan.steps:

            steps.append(
                WorkflowStep(
                    description=plan_step.description
                )
            )

        workflow = TemporaryWorkflow(
            task_id=task.id,
            steps=steps,
            experience_used=bool(memories),
        )

        print(
            f"[AI PLANNER] Validated AI plan "
            f"with {len(workflow.steps)} steps"
        )

        return workflow
