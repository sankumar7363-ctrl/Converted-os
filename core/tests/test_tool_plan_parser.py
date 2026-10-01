from core.executor.tool_plan_parser import ToolPlanParser


def main():

    print("\n=== TOOL PLAN PARSER TEST ===\n")

    parser = ToolPlanParser()

    # ---------------------------------------------
    # Valid AI response
    # ---------------------------------------------

    valid_response = """
{
    "goal": "Create a file called hello.txt",
    "calls": [
        {
            "tool_name": "create_file",
            "arguments": {
                "filename": "hello.txt",
                "content": "Hello Converted OS!"
            }
        }
    ]
}
"""

    plan = parser.parse(
        valid_response
    )

    print(
        f"[TEST] Goal: {plan.goal}"
    )

    print(
        f"[TEST] Tool: "
        f"{plan.calls[0].tool_name}"
    )

    print(
        f"[TEST] Arguments: "
        f"{plan.calls[0].arguments}"
    )

    assert (
        plan.goal
        == "Create a file called hello.txt"
    )

    assert (
        plan.calls[0].tool_name
        == "create_file"
    )

    assert (
        plan.calls[0].arguments["filename"]
        == "hello.txt"
    )

    assert (
        plan.calls[0].arguments["content"]
        == "Hello Converted OS!"
    )

    print(
        "[TEST] Valid tool plan parsed successfully"
    )

    # ---------------------------------------------
    # Invalid JSON
    # ---------------------------------------------

    print(
        "\n[TEST] Testing invalid JSON..."
    )

    try:

        parser.parse(
            "{ invalid json }"
        )

        raise AssertionError(
            "Invalid JSON was accepted"
        )

    except ValueError as error:

        print(
            f"[TEST] Invalid JSON rejected: "
            f"{error}"
        )

    # ---------------------------------------------
    # Invalid tool plan structure
    # ---------------------------------------------

    print(
        "\n[TEST] Testing invalid plan..."
    )

    try:

        parser.parse(
            """
            {
                "goal": "Create a file",
                "calls": [
                    {
                        "arguments": {}
                    }
                ]
            }
            """
        )

        raise AssertionError(
            "Invalid tool plan was accepted"
        )

    except ValueError as error:

        print(
            f"[TEST] Invalid plan rejected: "
            f"{error}"
        )

    print(
        "\n=== TOOL PLAN PARSER TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
