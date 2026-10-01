from core.ai.local_manager import LocalLLMManager
from core.ai.local_registry import LocalLLMStatus


def main():

    manager = LocalLLMManager()

    print("\n[TEST] Adding development models...")

    manager.add_model(
        name="Manager Test Small",
        runtime="ollama",
        endpoint="http://localhost:11434",
        model_id="manager-test-small",
        status=LocalLLMStatus.INSTALLED,
    )

    manager.add_model(
        name="Manager Test Advanced",
        runtime="ollama",
        endpoint="http://localhost:11434",
        model_id="manager-test-advanced",
        status=LocalLLMStatus.INSTALLED,
    )

    print("\n[TEST] Switching to advanced model...")

    switched = manager.switch_model(
        "manager-test-advanced"
    )

    current = manager.get_current_model()

    print(
        f"Switch result: {switched}"
    )

    print(
        f"Current model: "
        f"{current.name if current else None}"
    )

    if (
        current
        and current.model_id == "manager-test-advanced"
    ):
        print("[TEST] Switch: PASS")
    else:
        print("[TEST] Switch: FAIL")

    print("\n[TEST] Attempting to disable current model...")

    disabled_current = manager.disable_model(
        "manager-test-advanced"
    )

    print(
        f"Disable current result: "
        f"{disabled_current}"
    )

    if not disabled_current:
        print("[TEST] Current-model protection: PASS")
    else:
        print("[TEST] Current-model protection: FAIL")

    print("\n[TEST] Disabling non-current model...")

    disabled_other = manager.disable_model(
        "manager-test-small"
    )

    print(
        f"Disable other result: "
        f"{disabled_other}"
    )

    other = manager.get_model(
        "manager-test-small"
    )

    print(
        f"Other model status: "
        f"{other.status.value if other else None}"
    )

    if (
        other
        and other.status == LocalLLMStatus.DISABLED
    ):
        print("[TEST] Disable: PASS")
    else:
        print("[TEST] Disable: FAIL")

    print("\n[TEST] Marking model unavailable...")

    unavailable = manager.mark_unavailable(
        "manager-test-small"
    )

    print(
        f"Unavailable result: "
        f"{unavailable}"
    )

    print("\n[TEST] Removing non-current model...")

    removed = manager.remove_model(
        "manager-test-small"
    )

    print(
        f"Remove result: "
        f"{removed}"
    )

    if removed:
        print("[TEST] Remove: PASS")
    else:
        print("[TEST] Remove: FAIL")

    print("\n[TEST] Final model list:")

    for model in manager.list_models():

        print(
            f"- {model.name} | "
            f"{model.status.value} | "
            f"default: {model.default}"
        )


if __name__ == "__main__":
    main()
