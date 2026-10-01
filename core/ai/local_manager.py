from core.ai.local_registry import (
    LocalLLM,
    LocalLLMRegistry,
    LocalLLMStatus,
)


class LocalLLMManager:

    def __init__(self):

        self.registry = LocalLLMRegistry()

    def add_model(
        self,
        name: str,
        runtime: str,
        endpoint: str,
        model_id: str,
        default: bool = False,
        status: LocalLLMStatus = (
            LocalLLMStatus.REGISTERED
        ),
    ) -> LocalLLM:

        model = self.registry.add_model(
            name=name,
            runtime=runtime,
            endpoint=endpoint,
            model_id=model_id,
            default=default,
            status=status,
        )

        print(
            f"[LOCAL AI] Model added: "
            f"{model.name}"
        )

        return model

    def remove_model(
        self,
        model_id: str
    ) -> bool:

        current = self.get_current_model()

        if current and current.model_id == model_id:

            print(
                "[LOCAL AI] Cannot remove "
                "the current default model"
            )

            return False

        removed = self.registry.remove_model(
            model_id
        )

        if removed:

            print(
                f"[LOCAL AI] Model removed: "
                f"{model_id}"
            )

        else:

            print(
                f"[LOCAL AI] Model not found: "
                f"{model_id}"
            )

        return removed

    def switch_model(
        self,
        model_id: str
    ) -> bool:

        switched = self.registry.set_default(
            model_id
        )

        if switched:

            print(
                f"[LOCAL AI] Switched to model: "
                f"{model_id}"
            )

        else:

            print(
                f"[LOCAL AI] Unable to switch "
                f"to model: {model_id}"
            )

        return switched

    def get_current_model(
        self
    ) -> LocalLLM | None:

        return self.registry.get_default()

    def list_models(self) -> list[LocalLLM]:

        return self.registry.list_models()

    def get_model(
        self,
        model_id: str
    ) -> LocalLLM | None:

        return self.registry.get_model(
            model_id
        )

    def set_status(
        self,
        model_id: str,
        status: LocalLLMStatus
    ) -> bool:

        updated = self.registry.set_status(
            model_id,
            status
        )

        if updated:

            print(
                f"[LOCAL AI] Model status changed: "
                f"{model_id} -> {status.value}"
            )

        else:

            print(
                f"[LOCAL AI] Model not found: "
                f"{model_id}"
            )

        return updated

    def install_model(
        self,
        model_id: str
    ) -> bool:

        return self.set_status(
            model_id,
            LocalLLMStatus.INSTALLED
        )

    def disable_model(
        self,
        model_id: str
    ) -> bool:

        current = self.get_current_model()

        if current and current.model_id == model_id:

            print(
                "[LOCAL AI] Cannot disable "
                "the current default model"
            )

            return False

        return self.set_status(
            model_id,
            LocalLLMStatus.DISABLED
        )

    def mark_unavailable(
        self,
        model_id: str
    ) -> bool:

        return self.set_status(
            model_id,
            LocalLLMStatus.UNAVAILABLE
        )
