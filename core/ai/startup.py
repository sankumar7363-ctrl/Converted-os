from core.ai.local_registry import LocalLLMRegistry
from core.ai.local_sync import LocalAISynchronizer


class LocalAIStartup:

    def __init__(self):
        self.registry = LocalLLMRegistry()
        self.synchronizer = LocalAISynchronizer(
            registry=self.registry
        )

    def synchronize(self) -> list[str]:

        print("[LOCAL AI STARTUP] Synchronizing local AI")

        models = self.synchronizer.sync_ollama()

        print(
            "[LOCAL AI STARTUP] "
            f"Synchronization complete: {len(models)} model(s)"
        )

        return models
