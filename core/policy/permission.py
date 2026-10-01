from enum import Enum

from pydantic import BaseModel

from core.policy.policy import Action


class PermissionDecision(str, Enum):

    ALLOW = "allow"
    DENY = "deny"
    PENDING = "pending"


class PermissionRequest(BaseModel):

    task_id: str
    action: Action


class PermissionManager:

    def __init__(self):

        self.pending_actions: dict[
            str,
            PermissionRequest,
        ] = {}

    def request(
        self,
        task_id: str,
        action: Action,
    ) -> PermissionDecision:

        self.pending_actions[task_id] = (
            PermissionRequest(
                task_id=task_id,
                action=action,
            )
        )

        print(
            "[PERMISSION] Confirmation required:"
        )

        print(
            f"[PERMISSION] "
            f"{action.description}"
        )

        print(
            f"[PERMISSION] Task: "
            f"{task_id}"
        )

        return PermissionDecision.PENDING

    def approve(
        self,
        task_id: str,
    ) -> bool:

        if task_id not in self.pending_actions:
            return False

        del self.pending_actions[task_id]

        print(
            f"[PERMISSION] Approved: "
            f"{task_id}"
        )

        return True

    def deny(
        self,
        task_id: str,
    ) -> bool:

        if task_id not in self.pending_actions:
            return False

        del self.pending_actions[task_id]

        print(
            f"[PERMISSION] Denied: "
            f"{task_id}"
        )

        return True

    def is_pending(
        self,
        task_id: str,
    ) -> bool:

        return task_id in self.pending_actions

    def list_pending(self) -> list[PermissionRequest]:

        return list(
            self.pending_actions.values()
        )
