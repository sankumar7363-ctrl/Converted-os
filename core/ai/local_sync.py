from core.ai.local_registry import (
    LocalLLMRegistry,
    LocalLLMStatus,
)
from core.ai.runtime_detector import (
    LocalRuntimeDetector,
)


class LocalAISynchronizer:

    def __init__(
        self,
        registry: LocalLLMRegistry | None = None,
    ):

        self.registry = (
            registry
            if registry
            else LocalLLMRegistry()
        )

    def sync_ollama(
        self,
        endpoint: str = "http://localhost:11434",
    ) -> list[str]:

        detector = LocalRuntimeDetector(
            runtime="ollama",
            endpoint=endpoint,
        )

        print(
            "[LOCAL AI SYNC] Checking Ollama..."
        )

        # Important:
        # Do not modify model statuses when
        # the runtime itself is unavailable.
        if not detector.is_available():

            print(
                "[LOCAL AI SYNC] Ollama unavailable"
            )

            return []

        detected_models = (
            detector.list_models()
        )

        print(
            "[LOCAL AI SYNC] Detected models:"
        )

        for model_name in detected_models:

            print(
                f"- {model_name}"
            )

            existing = self.registry.get_model(
                model_name
            )

            if existing is None:

                self.registry.add_model(
                    name=model_name,
                    runtime="ollama",
                    endpoint=endpoint,
                    model_id=model_name,
                    status=LocalLLMStatus.INSTALLED,
                )

                print(
                    f"[LOCAL AI SYNC] Registered: "
                    f"{model_name}"
                )

            elif existing.status != (
                LocalLLMStatus.INSTALLED
            ):

                self.registry.set_status(
                    model_name,
                    LocalLLMStatus.INSTALLED,
                )

                print(
                    f"[LOCAL AI SYNC] Updated: "
                    f"{model_name}"
                )

        # Reconcile only models belonging to
        # the runtime we successfully checked.
        registered_models = self.registry.list_models()

        detected_set = set(detected_models)

        for model in registered_models:

            if model.runtime != "ollama":
                continue

            if model.model_id in detected_set:
                continue

            if model.status == LocalLLMStatus.INSTALLED:

                self.registry.set_status(
                    model.model_id,
                    LocalLLMStatus.UNAVAILABLE,
                )

                print(
                    f"[LOCAL AI SYNC] Marked unavailable: "
                    f"{model.model_id}"
                )

        return detected_models
