from core.executor.tool_argument_validator import (
    ToolArgumentValidator,
)

from core.executor.tool_definition import (
    ToolDefinition,
    ToolParameter,
    ToolRisk,
)


def main():

    print(
        "\n=== TOOL ARGUMENT VALIDATOR TEST ===\n"
    )

    validator = ToolArgumentValidator()

    tool = ToolDefinition(
        name="create_file",
        description="Create a file",
        risk=ToolRisk.LOW,
        parameters=[
            ToolParameter(
                name="filename",
                description="File name",
            ),
            ToolParameter(
                name="content",
                description="File content",
            ),
        ],
    )

    # -----------------------------------------
    # Valid arguments
    # -----------------------------------------

    print("[TEST] Valid arguments...")

    validator.validate(
        tool,
        {
            "filename": "hello.txt",
            "content": "Hello Converted OS!",
        },
    )

    print(
        "[TEST] Valid arguments accepted"
    )

    # -----------------------------------------
    # Missing parameter
    # -----------------------------------------

    print(
        "\n[TEST] Missing required parameter..."
    )

    try:

        validator.validate(
            tool,
            {
                "filename": "hello.txt",
            },
        )

        raise AssertionError(
            "Missing parameter was not rejected"
        )

    except ValueError as error:

        print(
            f"[TEST] Correctly rejected: {error}"
        )

    # -----------------------------------------
    # Unknown parameter
    # -----------------------------------------

    print(
        "\n[TEST] Unknown parameter..."
    )

    try:

        validator.validate(
            tool,
            {
                "filename": "hello.txt",
                "content": "Hello",
                "unknown": "bad",
            },
        )

        raise AssertionError(
            "Unknown parameter was not rejected"
        )

    except ValueError as error:

        print(
            f"[TEST] Correctly rejected: {error}"
        )

    # -----------------------------------------
    # Non-dictionary arguments
    # -----------------------------------------

    print(
        "\n[TEST] Invalid argument object..."
    )

    try:

        validator.validate(
            tool,
            "invalid",
        )

        raise AssertionError(
            "Invalid argument object was not rejected"
        )

    except ValueError as error:

        print(
            f"[TEST] Correctly rejected: {error}"
        )

    print(
        "\n=== TOOL ARGUMENT VALIDATOR TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
