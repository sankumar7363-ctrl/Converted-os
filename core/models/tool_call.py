from typing import Any

from pydantic import BaseModel, Field


class ToolCall(BaseModel):

    tool_name: str

    arguments: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )


class ToolPlan(BaseModel):

    goal: str

    calls: list[
        ToolCall
    ] = Field(
        default_factory=list
    )
