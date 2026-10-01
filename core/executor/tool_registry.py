from typing import Any, Callable


class ToolRegistry:

    def __init__(self):

        self.tools: dict[
            str,
            Callable[..., Any],
        ] = {}

    def register(
        self,
        name: str,
        tool: Callable[..., Any],
    ) -> None:

        if name in self.tools:
            raise ValueError(
                f"Tool already registered: {name}"
            )

        self.tools[name] = tool

        print(
            f"[TOOLS] Registered: {name}"
        )

    def unregister(
        self,
        name: str,
    ) -> bool:

        if name not in self.tools:
            return False

        del self.tools[name]

        print(
            f"[TOOLS] Unregistered: {name}"
        )

        return True

    def get(
        self,
        name: str,
    ) -> Callable[..., Any] | None:

        return self.tools.get(name)

    def has(
        self,
        name: str,
    ) -> bool:

        return name in self.tools

    def list_tools(self) -> list[str]:

        return sorted(
            self.tools.keys()
        )

    def execute(
        self,
        name: str,
        **kwargs,
    ) -> Any:

        tool = self.get(name)

        if tool is None:
            raise ValueError(
                f"Unknown tool: {name}"
            )

        print(
            f"[TOOLS] Executing: {name}"
        )

        return tool(**kwargs)
