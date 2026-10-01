from typing import Any, Callable

from core.executor.tool_definition import (
    ToolDefinition,
)


class ToolCatalog:

    def __init__(self):

        self.definitions: dict[
            str,
            ToolDefinition,
        ] = {}

        self.implementations: dict[
            str,
            Callable[..., Any],
        ] = {}

    def register(
        self,
        definition: ToolDefinition,
        implementation: Callable[..., Any],
    ) -> None:

        if definition.name in self.definitions:

            raise ValueError(
                f"Tool already registered: "
                f"{definition.name}"
            )

        self.definitions[
            definition.name
        ] = definition

        self.implementations[
            definition.name
        ] = implementation

        print(
            f"[CATALOG] Registered: "
            f"{definition.name}"
        )

    def get_definition(
        self,
        name: str,
    ) -> ToolDefinition | None:

        return self.definitions.get(name)

    def get_implementation(
        self,
        name: str,
    ) -> Callable[..., Any] | None:

        return self.implementations.get(name)

    def has(
        self,
        name: str,
    ) -> bool:

        return name in self.definitions

    def list_tools(self) -> list[str]:

        return sorted(
            self.definitions.keys()
        )

    def describe_tools(
        self,
    ) -> list[ToolDefinition]:

        return list(
            self.definitions.values()
        )

    def unregister(
        self,
        name: str,
    ) -> bool:

        if name not in self.definitions:

            return False

        del self.definitions[name]
        del self.implementations[name]

        print(
            f"[CATALOG] Unregistered: "
            f"{name}"
        )

        return True
