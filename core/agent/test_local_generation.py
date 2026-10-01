from config.ai_config import AIConfig
from core.ai.provider import create_ai_model


def main():

    config = AIConfig.from_environment()

    print("\n[LOCAL AI GENERATION TEST]")

    try:

        model = create_ai_model(config)

        print(
            f"[TEST] Selected model: "
            f"{model.model}"
        )

        response = model.generate(
            "Reply with exactly: Converted OS local AI test successful"
        )

        print("\n[TEST] Model response:")
        print(response)

        print(
            "\n[LOCAL AI GENERATION TEST] PASS"
        )

    except Exception as error:

        print(
            "\n[LOCAL AI GENERATION TEST] "
            "Runtime unavailable"
        )

        print(
            f"[TEST] Reason: {error}"
        )


if __name__ == "__main__":
    main()
