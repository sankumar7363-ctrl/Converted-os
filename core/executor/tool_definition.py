from enum import Enum

from pydantic import BaseModel


class ToolRisk(str, Enum):

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolParameter(BaseModel):

    name: str
    description: str
    required: bool = True


class ToolDefinition(BaseModel):

    name: str
    description: str
    risk: ToolRisk

    parameters: list[
        ToolParameter
    ] = []

    autonomous: bool = True
