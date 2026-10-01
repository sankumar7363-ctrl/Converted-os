from typing import Any

from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_executor import ToolExecutor
from core.executor.tool_selector import ToolSelector
from core.executor.safe_tool_executor import SafeToolExecutor
from core.executor.tool_policy import ToolPolicy

from core.executor.tool_registry import ToolRegistry
from core.policy.permission import PermissionManager


class ToolSystem:

    def __init__(self):

        # Tool registration
        self.registry = ToolRegistry()

        # Tool metadata
        self.catalog = ToolCatalog()

        # Tool discovery and selection
        self.selector = ToolSelector(
            catalog=self.catalog
        )

        # Basic execution
        self.executor = ToolExecutor(
            registry=self.registry
        )

        # Policy
        self.policy = ToolPolicy()

        # Permission management
        self.permissions = PermissionManager()

        # Safe execution
        self.safe_executor = SafeToolExecutor(
            catalog=self.catalog,
            executor=self.executor,
            policy=self.policy,
            permissions=self.permissions,
        )

    def register(
        self,
        definition,
        implementation,
    ) -> None:

        self.registry.register(
            name=definition.name,
            tool=implementation,
        )

        self.catalog.register(
            definition=definition,
            implementation=implementation,
        )

    def available_tools(self) -> list[str]:

        return self.catalog.list_tools()

    def find_tools(
        self,
        goal: str,
    ):

        return self.selector.select(
            goal
        )

    def execute(
        self,
        task_id: str,
        goal: str,
        **kwargs: Any,
    ):

        selected_tools = self.find_tools(
            goal
        )

        if not selected_tools:

            raise ValueError(
                f"No suitable tool found for: "
                f"{goal}"
            )

        tool = selected_tools[0]

        print(
            f"[TOOL SYSTEM] Selected: "
            f"{tool.name}"
        )

        return self.safe_executor.execute(
            task_id=task_id,
            tool_name=tool.name,
            **kwargs,
        )
