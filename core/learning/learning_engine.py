from core.models.experience import (
    Experience,
    ExperienceStep,
    LearningSignal,
    OutcomeStatus,
)
from memory.store import MemoryStore


class LearningEngine:
    def __init__(self, memory: MemoryStore | None = None):
        self.memory = memory if memory is not None else MemoryStore()

    def create_experience(
        self,
        goal: str,
        results: list,
        recovery_used: bool = False,
    ) -> Experience:
        steps = []

        for index, result in enumerate(results):
            if isinstance(result, dict):
                step_index = result.get("step_index", index)
                tool_name = result.get("tool")
                success = result.get("success", False)

                if result.get("status") == "success":
                    success = True

                error = result.get("error")

                description = result.get(
                    "description",
                    f"Tool execution step {step_index}",
                )
            else:
                step_index = getattr(result, "step_index", index)
                tool_name = getattr(result, "tool_name", None)
                success = getattr(result, "success", False)
                error = getattr(result, "error", None)

                description = f"Tool execution step {step_index}"

            steps.append(
                ExperienceStep(
                    step_index=step_index,
                    description=description,
                    tool_name=tool_name,
                    success=success,
                    error=error,
                )
            )

        successful_steps = sum(1 for step in steps if step.success)
        failed_steps = len(steps) - successful_steps

        if steps and failed_steps == 0:
            outcome = OutcomeStatus.SUCCESS
            summary = "Task completed successfully."
            useful = True
            reason = "The workflow completed without unresolved failures."
            improvement = None

        elif successful_steps > 0:
            outcome = OutcomeStatus.PARTIAL
            summary = "Task completed partially."
            useful = True
            reason = "The workflow produced useful results but encountered failures."
            improvement = "Improve failed steps and recovery strategies."

        else:
            outcome = OutcomeStatus.FAILURE
            summary = "Task failed."
            useful = False
            reason = "The workflow did not produce a successful result."
            improvement = "Find an alternative execution strategy."

        learning_signal = LearningSignal(
            useful=useful,
            reason=reason,
            improvement=improvement,
        )

        return Experience(
            goal=goal,
            steps=steps,
            outcome=outcome,
            summary=summary,
            recovery_used=recovery_used,
            learning_signal=learning_signal,
        )

    def store_experience(
        self,
        experience: Experience,
    ):

        learning_content = (
            f"Goal: {experience.goal} | "
            f"Outcome: {experience.outcome.value} | "
            f"Summary: {experience.summary} | "
            f"Recovery used: {experience.recovery_used}"
        )

        if experience.steps:

            step_details = []

            for step in experience.steps:

                step_text = (
                    f"Step {step.step_index}: "
                    f"{step.description} | "
                    f"Tool: {step.tool_name} | "
                    f"Success: {step.success}"
                )

                if step.error:

                    step_text += (
                        f" | Error: {step.error}"
                    )

                step_details.append(
                    step_text
                )

            learning_content += (
                " | Steps: "
                + " || ".join(step_details)
            )

        if experience.learning_signal is not None:

            learning_content += (
                f" | Learning: "
                f"{experience.learning_signal.reason}"
            )

            if experience.learning_signal.improvement:

                learning_content += (
                    f" | Improvement: "
                    f"{experience.learning_signal.improvement}"
                )

        return self.memory.remember(
            memory_type="experience",
            content=learning_content,
        )

    def find_relevant_experiences(
        self,
        goal: str,
        limit: int = 5,
    ):
        return self.memory.search(
            query=goal,
            limit=limit,
        )
