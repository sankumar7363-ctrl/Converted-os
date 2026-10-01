from core.executor.tools.terminal_tools import TerminalTools


def test_terminal_failure():
    terminal = TerminalTools()

    result = terminal.run_command(
        "bash -c 'echo failure-message >&2; exit 7'",
        timeout=10,
    )

    assert result["success"] is False
    assert result["timed_out"] is False
    assert result["return_code"] == 7
    assert "failure-message" in result["stderr"]

    print("\n=== TERMINAL FAILURE TEST PASSED ===")
    print(result)


def test_terminal_timeout():
    terminal = TerminalTools()

    result = terminal.run_command(
        "sleep 2",
        timeout=1,
    )

    assert result["success"] is False
    assert result["timed_out"] is True
    assert result["return_code"] is None

    print("\n=== TERMINAL TIMEOUT TEST PASSED ===")
    print(result)


if __name__ == "__main__":
    test_terminal_failure()
    test_terminal_timeout()
    print("\n=== ALL TERMINAL FAILURE TESTS PASSED ===")
