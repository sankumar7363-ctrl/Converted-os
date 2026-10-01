from tools.file_tool import FileTool


class FileTools:

    def __init__(
        self,
        workspace: str = "workspace",
    ):

        self.file_tool = FileTool(
            workspace=workspace
        )

    def create_file(
        self,
        filename: str,
        content: str,
    ) -> str:

        path = self.file_tool.create_file(
            filename=filename,
            content=content,
        )

        print(
            f"[FILE TOOL] File created: {path}"
        )

        return path

    def read_file(
        self,
        filename: str,
    ) -> str:

        content = self.file_tool.read_file(
            filename=filename
        )

        print(
            f"[FILE TOOL] File read: {filename}"
        )

        return content
