from pathlib import Path

from core.observer.file_observer import (
    FileObserver,
)


def main():

    print(
        "\n=== FILE OBSERVER TEST ===\n"
    )

    workspace = Path(
        "workspace/observer_test"
    )

    workspace.mkdir(
        parents=True,
        exist_ok=True,
    )

    filepath = (
        workspace / "observed.txt"
    )

    filepath.write_text(
        "Converted OS observer test",
        encoding="utf-8",
    )

    observer = FileObserver()

    print(
        "[TEST] Checking existence..."
    )

    assert observer.exists(
        str(filepath)
    )

    print(
        "[TEST] File exists"
    )

    print(
        "[TEST] Checking file type..."
    )

    assert observer.is_file(
        str(filepath)
    )

    print(
        "[TEST] Path is a file"
    )

    print(
        "[TEST] Checking content..."
    )

    content = observer.read_content(
        str(filepath)
    )

    print(
        f"[TEST] Content: {content}"
    )

    assert (
        content
        == "Converted OS observer test"
    )

    print(
        "[TEST] Content is correct"
    )

    print(
        "[TEST] Running complete verification..."
    )

    verified = observer.verify_file(
        filepath=str(filepath),
        expected_content=(
            "Converted OS observer test"
        ),
    )

    assert verified

    print(
        "\n[TEST] File observation successful"
    )

    print(
        "\n=== FILE OBSERVER TEST PASSED ==="
    )


if __name__ == "__main__":
    main()
