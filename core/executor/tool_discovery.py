from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_definition import ToolDefinition


class ToolDiscovery:

    def __init__(
        self,
        catalog: ToolCatalog,
    ):

        self.catalog = catalog

    def list_tools(self) -> list[ToolDefinition]:

        return self.catalog.describe_tools()

    def find_tool(
        self,
        name: str,
    ) -> ToolDefinition | None:

        return self.catalog.get_definition(name)

    def describe(
        self,
        name: str,
    ) -> str | None:

        tool = self.find_tool(name)

        if tool is None:
            return None

        parameters = ", ".join(
            parameter.name
            for parameter in tool.parameters
        )

        return (
            f"Tool: {tool.name}\n"
            f"Description: {tool.description}\n"
            f"Risk: {tool.risk.value}\n"
            f"Autonomous: {tool.autonomous}\n"
            f"Parameters: {parameters}"
        )
