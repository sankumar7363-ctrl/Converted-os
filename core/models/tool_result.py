from enum import Enum
from typing import Any

from pydantic import BaseModel


class ToolResultStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING_PERMISSION = "pending_permission"


class ToolCallResult(BaseModel):
    step_index: int
    tool_name: str
    status: ToolResultStatus
    success: bool
    result: Any | None = None
    error: str | None = None
