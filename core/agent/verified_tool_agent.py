from pathlib import Path
from typing import Any

from core.agent.tool_agent import ToolAgent
from core.observer.file_observer import FileObserver


class VerifiedToolAgent:

    def __init__(
        self,
        tool_agent: ToolAgent,
        file_observer: FileObserver,
    ):

        self.tool_agent = tool_agent
        self.file_observer = file_observer

    def run(
        self,
        task_id: str,
        goal: str,
        expected_file: str | None = None,
        expected_content: str | None = None,
    ) -> dict[str, Any]:

        print(
            f"\n[VERIFIED AGENT] Goal: {goal}"
        )

        results = self.tool_agent.run(
            task_id=task_id,
            goal=goal,
        )

        if expected_file is None:

            print(
                "[VERIFIED AGENT] "
                "No file verification requested"
            )

            return {
                "success": True,
                "results": results,
                "verified": False,
            }

        print(
            "[VERIFIED AGENT] "
            f"Verifying file: {expected_file}"
        )

        verified = self.file_observer.verify_file(
            filepath=expected_file,
            expected_content=expected_content,
        )

        if verified:

            print(
                "[VERIFIED AGENT] "
                "Result verified successfully"
            )

        else:

            print(
                "[VERIFIED AGENT] "
                "Result verification failed"
            )

        return {
            "success": verified,
            "results": results,
            "verified": verified,
        }
