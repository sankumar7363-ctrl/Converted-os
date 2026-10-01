from config.ai_config import AIConfig, AIProvider
from core.ai.provider import create_ai_model
from core.ai.local_registry import (
    LocalLLMRegistry,
    LocalLLMStatus,
)


def main():

    registry = LocalLLMRegistry()

    print("\n[TEST] Current models:")

    for model in registry.list_models():
        print(
            f"- {model.name} | "
            f"{model.status.value} | "
            f"default: {model.default}"
        )

    # Make sure we have two installed models
    registry.add_model(
        name="Small Model",
        runtime="ollama",
        endpoint="http://localhost:11434",
        model_id="small-model",
        status=LocalLLMStatus.INSTALLED,
        default=True,
    )

    registry.add_model(
        name="Advanced Model",
        runtime="ollama",
        endpoint="http://localhost:11434",
        model_id="advanced-model",
        status=LocalLLMStatus.INSTALLED,
        default=False,
    )

    # User selects Advanced Model
    print("\n[TEST] Selecting Advanced Model...")

    registry.set_default(
        "advanced-model"
    )

    selected = registry.get_default()

    print(
        f"[TEST] Selected: "
        f"{selected.name if selected else None}"
    )

    # Simulate Converted OS starting again
    config = AIConfig(
        provider=AIProvider.LOCAL,
        local_model="small-model",
        local_runtime="ollama",
        local_endpoint="http://localhost:11434",
    )

    print(
        "\n[TEST] Starting AI provider..."
    )

    model = create_ai_model(config)

    print(
        f"[TEST] Provider returned model: "
        f"{model.model}"
    )

    # Verify persistence
    if model.model == "advanced-model":

        print(
            "\n[PERSISTENCE TEST] PASS"
        )

        print(
            "[PERSISTENCE TEST] "
            "Selected model survived provider startup."
        )

    else:

        print(
            "\n[PERSISTENCE TEST] FAIL"
        )

        print(
            "[PERSISTENCE TEST] "
            "Provider changed the selected model."
        )


if __name__ == "__main__":
    main()
