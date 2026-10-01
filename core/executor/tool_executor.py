from typing import Any

from core.executor.tool_registry import ToolRegistry


class ToolExecutor:

    def __init__(
        self,
        registry: ToolRegistry,
    ):

        self.registry = registry

    def execute(
        self,
        tool_name: str,
        **kwargs: Any,
    ) -> Any:

        if not self.registry.has(tool_name):

            raise ValueError(
                f"Tool not available: "
                f"{tool_name}"
            )

        print(
            f"[TOOL EXECUTOR] "
            f"Executing: {tool_name}"
        )

        return self.registry.execute(
            tool_name,
            **kwargs,
        )
