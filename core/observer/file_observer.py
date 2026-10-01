from pathlib import Path


class FileObserver:

    def exists(
        self,
        filepath: str,
    ) -> bool:

        path = Path(filepath)

        return path.exists()

    def is_file(
        self,
        filepath: str,
    ) -> bool:

        path = Path(filepath)

        return path.is_file()

    def read_content(
        self,
        filepath: str,
    ) -> str:

        path = Path(filepath)

        if not path.exists():

            raise FileNotFoundError(
                f"File not found: {filepath}"
            )

        if not path.is_file():

            raise ValueError(
                f"Path is not a file: {filepath}"
            )

        return path.read_text(
            encoding="utf-8"
        )

    def verify_content(
        self,
        filepath: str,
        expected_content: str,
    ) -> bool:

        try:

            actual_content = self.read_content(
                filepath
            )

        except (
            FileNotFoundError,
            ValueError,
        ):

            return False

        return (
            actual_content
            == expected_content
        )

    def verify_file(
        self,
        filepath: str,
        expected_content: str | None = None,
    ) -> bool:

        if not self.exists(filepath):

            print(
                f"[FILE OBSERVER] "
                f"File does not exist: {filepath}"
            )

            return False

        if not self.is_file(filepath):

            print(
                f"[FILE OBSERVER] "
                f"Path is not a file: {filepath}"
            )

            return False

        if expected_content is not None:

            if not self.verify_content(
                filepath,
                expected_content,
            ):

                print(
                    f"[FILE OBSERVER] "
                    f"Content verification failed: "
                    f"{filepath}"
                )

                return False

        print(
            f"[FILE OBSERVER] "
            f"File verified: {filepath}"
        )

        return True
