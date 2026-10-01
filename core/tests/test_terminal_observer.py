from core.executor.tools.terminal_tools import TerminalTools
from core.observer.tool_observer import ToolObserver


def test_terminal_success_observation():
    terminal = TerminalTools()
    observer = ToolObserver()

    result = terminal.run_command(
        "echo Converted OS",
        timeout=10,
    )

    observation = observer.observe_success(
        step_index=0,
        tool_name="run_command",
        result=result,
    )

    assert observation.success is True
    assert observation.tool_name == "run_command"
    assert observation.step_index == 0
    assert observation.result["success"] is True
    assert "Converted OS" in observation.result["stdout"]

    print("\n=== TERMINAL SUCCESS OBSERVATION PASSED ===")
    print(observation)


def test_terminal_failure_observation():
    terminal = TerminalTools()
    observer = ToolObserver()

    result = terminal.run_command(
        "bash -c 'echo terminal-error >&2; exit 7'",
        timeout=10,
    )

    observation = observer.observe_failure(
        step_index=0,
        tool_name="run_command",
        error=RuntimeError(
            f"Command failed with exit code {result['return_code']}: "
            f"{result['stderr'].strip()}"
        ),
    )

    assert observation.success is False
    assert observation.tool_name == "run_command"
    assert observation.step_index == 0
    assert "exit code 7" in observation.error
    assert "terminal-error" in observation.error

    print("\n=== TERMINAL FAILURE OBSERVATION PASSED ===")
    print(observation)


def test_terminal_timeout_observation():
    terminal = TerminalTools()
    observer = ToolObserver()

    result = terminal.run_command(
        "sleep 2",
        timeout=1,
    )

    observation = observer.observe_failure(
        step_index=0,
        tool_name="run_command",
        error=TimeoutError(
            "Terminal command timed out"
        ),
    )

    assert observation.success is False
    assert observation.tool_name == "run_command"
    assert observation.step_index == 0
    assert "timed out" in observation.error

    print("\n=== TERMINAL TIMEOUT OBSERVATION PASSED ===")
    print(observation)


if __name__ == "__main__":
    test_terminal_success_observation()
    test_terminal_failure_observation()
    test_terminal_timeout_observation()

    print("\n=== ALL TERMINAL OBSERVER TESTS PASSED ===")
