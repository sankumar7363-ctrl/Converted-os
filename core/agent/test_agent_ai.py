from config.ai_config import AIConfig
from core.ai.provider import create_ai_model


def main():

    config = AIConfig.from_environment()

    print("\n[AGENT AI TEST]")
    print(
        f"Provider: {config.provider.value}"
    )

    try:

        model = create_ai_model(config)

        print(
            f"AI model type: "
            f"{type(model).__name__}"
        )

        print(
            "[AGENT AI TEST] "
            "AI provider connected successfully"
        )

    except Exception as error:

        print(
            "[AGENT AI TEST] "
            "AI provider unavailable"
        )

        print(
            f"Reason: {error}"
        )


if __name__ == "__main__":
    main()
