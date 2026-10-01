from pathlib import Path


class FileTool:

    def __init__(self, workspace: str = "workspace"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)

    def create_file(self, filename: str, content: str = "") -> str:
        path = self.workspace / filename

        # Prevent paths from escaping the workspace.
        if ".." in Path(filename).parts:
            raise ValueError("Invalid file path")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        return str(path)

    def read_file(self, filename: str) -> str:
        path = self.workspace / filename

        if ".." in Path(filename).parts:
            raise ValueError("Invalid file path")

        return path.read_text(encoding="utf-8")
