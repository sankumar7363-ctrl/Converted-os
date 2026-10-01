import subprocess


class TerminalTools:

    def __init__(
        self,
        workspace: str = "workspace",
    ):

        self.workspace = workspace

    def run_command(
        self,
        command: str,
        timeout: int = 10,
    ) -> dict:

        if not command.strip():
            raise ValueError(
                "Command cannot be empty"
            )

        if timeout <= 0:
            raise ValueError(
                "Timeout must be greater than zero"
            )

        print(
            f"[TERMINAL] Running: {command}"
        )

        try:

            completed = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

        except subprocess.TimeoutExpired as error:

            print(
                "[TERMINAL] Command timed out"
            )

            return {
                "success": False,
                "timed_out": True,
                "return_code": None,
                "stdout": (
                    error.stdout
                    if error.stdout
                    else ""
                ),
                "stderr": (
                    error.stderr
                    if error.stderr
                    else ""
                ),
            }

        print(
            f"[TERMINAL] Exit code: "
            f"{completed.returncode}"
        )

        return {
            "success": (
                completed.returncode == 0
            ),
            "timed_out": False,
            "return_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
