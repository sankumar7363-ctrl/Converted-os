from core.ai.model import AIModel

from core.executor.tool_discovery import (
    ToolDiscovery,
)

from core.executor.tool_plan_parser import (
    ToolPlanParser,
)

from core.models.tool_call import (
    ToolPlan,
)


class ToolPlanningAgent:

    def __init__(
        self,
        ai_model: AIModel,
        discovery: ToolDiscovery,
    ):

        self.ai_model = ai_model
        self.discovery = discovery
        self.parser = ToolPlanParser()

    def _build_prompt(
        self,
        goal: str,
    ) -> str:

        tools = self.discovery.list_tools()

        tool_descriptions = []

        for tool in tools:

            parameters = []

            for parameter in tool.parameters:

                required = (
                    "required"
                    if parameter.required
                    else "optional"
                )

                parameters.append(
                    f"- {parameter.name}: "
                    f"{parameter.description} "
                    f"({required})"
                )

            parameter_text = (
                "\n".join(parameters)
                if parameters
                else "None"
            )

            tool_descriptions.append(
                f"Tool: {tool.name}\n"
                f"Description: {tool.description}\n"
                f"Risk: {tool.risk.value}\n"
                f"Parameters:\n"
                f"{parameter_text}"
            )

        available_tools = (
            "\n\n".join(tool_descriptions)
            if tool_descriptions
            else "No tools available."
        )

        return f"""
You are the planning component of Converted OS.

The user has provided this goal:

{goal}

Available tools:

{available_tools}

Create a JSON tool plan that can accomplish the user's goal.

The response MUST contain only valid JSON.

Use this structure:

{{
    "goal": "{goal}",
    "calls": [
        {{
            "tool_name": "tool_name",
            "arguments": {{}}
        }}
    ]
}}

Rules:

1. Only use tools from the available tools list.
2. Use the exact tool names.
3. Use the exact parameter names.
4. Include all required parameters.
5. Do not invent tools.
6. Do not invent parameters.
7. Do not include explanations outside the JSON.
""".strip()

    def create_plan(
        self,
        goal: str,
    ) -> ToolPlan:

        prompt = self._build_prompt(goal)

        print(
            "[TOOL PLANNER] "
            "Generating tool plan"
        )

        response = self.ai_model.generate(
            prompt
        )

        print(
            "[TOOL PLANNER] "
            "Parsing AI response"
        )

        plan = self.parser.parse(
            response
        )

        print(
            "[TOOL PLANNER] "
            f"Plan created with "
            f"{len(plan.calls)} tool call(s)"
        )

        return plan
