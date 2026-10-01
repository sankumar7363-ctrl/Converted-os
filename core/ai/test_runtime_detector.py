from core.ai.runtime_detector import (
    LocalRuntimeDetector,
)


def main():

    detector = LocalRuntimeDetector(
        runtime="ollama",
        endpoint="http://localhost:11434",
    )

    available = detector.is_available()

    print(
        f"[RUNTIME TEST] Ollama available: "
        f"{available}"
    )

    models = detector.list_models()

    print(
        f"[RUNTIME TEST] Models detected: "
        f"{models}"
    )


if __name__ == "__main__":
    main()
