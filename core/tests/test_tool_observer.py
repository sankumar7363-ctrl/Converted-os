from core.observer.tool_observer import ToolObserver


def main():

    print(
        "\n=== TOOL OBSERVER TEST ===\n"
    )

    observer = ToolObserver()

    success = observer.observe_success(
        step_index=0,
        tool_name="create_file",
        result="workspace/index.html",
    )

    assert success.success is True
    assert success.step_index == 0
    assert success.tool_name == "create_file"
    assert success.result == (
        "workspace/index.html"
    )
    assert success.error is None

    failure = observer.observe_failure(
        step_index=1,
        tool_name="create_file",
        error=ValueError(
            "File content is invalid"
        ),
    )

    assert failure.success is False
    assert failure.step_index == 1
    assert failure.tool_name == "create_file"
    assert failure.result is None
    assert failure.error == (
        "File content is invalid"
    )

    print(
        "\n[TEST] Success observation verified"
    )

    print(
        "[TEST] Failure observation verified"
    )

    print(
        "\n=== TOOL OBSERVER TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
