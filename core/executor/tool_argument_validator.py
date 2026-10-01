from typing import Any

from core.executor.tool_definition import (
    ToolDefinition,
)


class ToolArgumentValidator:

    def validate(
        self,
        tool: ToolDefinition,
        arguments: dict[str, Any],
    ) -> None:

        if not isinstance(arguments, dict):

            raise ValueError(
                f"Arguments for tool "
                f"{tool.name} must be an object"
            )

        declared_parameters = {
            parameter.name: parameter
            for parameter in tool.parameters
        }

        # -----------------------------------------
        # Check for unknown parameters
        # -----------------------------------------

        unknown_parameters = (
            set(arguments)
            - set(declared_parameters)
        )

        if unknown_parameters:

            names = ", ".join(
                sorted(unknown_parameters)
            )

            raise ValueError(
                f"Unknown parameter(s) for "
                f"{tool.name}: {names}"
            )

        # -----------------------------------------
        # Check required parameters
        # -----------------------------------------

        missing_parameters = []

        for parameter in tool.parameters:

            if (
                parameter.required
                and parameter.name not in arguments
            ):

                missing_parameters.append(
                    parameter.name
                )

        if missing_parameters:

            names = ", ".join(
                missing_parameters
            )

            raise ValueError(
                f"Missing required parameter(s) "
                f"for {tool.name}: {names}"
            )

        print(
            f"[ARGUMENT VALIDATOR] "
            f"Arguments valid: {tool.name}"
        )
