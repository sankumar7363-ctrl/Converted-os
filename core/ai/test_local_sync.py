from core.ai.local_sync import (
    LocalAISynchronizer,
)


def main():

    synchronizer = LocalAISynchronizer()

    models = synchronizer.sync_ollama()

    print(
        "\n[SYNC TEST] Models synchronized:"
    )

    for model in models:

        print(
            f"- {model}"
        )


if __name__ == "__main__":
    main()
