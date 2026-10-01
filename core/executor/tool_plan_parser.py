import json

from core.models.tool_call import ToolPlan


class ToolPlanParser:

    def parse(
        self,
        response: str,
    ) -> ToolPlan:

        if not response.strip():

            raise ValueError(
                "AI tool plan response is empty"
            )

        try:

            data = json.loads(response)

        except json.JSONDecodeError as error:

            raise ValueError(
                "AI returned invalid JSON"
            ) from error

        try:

            return ToolPlan.model_validate(
                data
            )

        except Exception as error:

            raise ValueError(
                "AI returned an invalid tool plan"
            ) from error
