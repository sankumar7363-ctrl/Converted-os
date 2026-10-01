from config.ai_config import AIConfig, AIProvider

from core.ai.test_model import TestAIModel
from core.ai.cloud_model import CloudAIModel
from core.ai.local_model import LocalAIModel
from core.ai.local_registry import (
    LocalLLMRegistry,
    LocalLLMStatus,
)
from core.ai.runtime_detector import LocalRuntimeDetector


def create_ai_model(config: AIConfig):

    if config.provider == AIProvider.TEST:

        return TestAIModel()

    if config.provider == AIProvider.LOCAL:

        registry = LocalLLMRegistry()

        current_model = registry.get_default()

        if current_model is None:

            raise ValueError(
                "No installed local AI model is selected"
            )

        print(
            "[LOCAL AI] Checking runtime: "
            f"{current_model.runtime}"
        )

        detector = LocalRuntimeDetector(
            runtime=current_model.runtime,
            endpoint=current_model.endpoint,
        )

        if not detector.is_available():

            registry.set_status(
                current_model.model_id,
                LocalLLMStatus.UNAVAILABLE,
            )

            raise RuntimeError(
                f"Local AI runtime unavailable: "
                f"{current_model.runtime}"
            )

        available_models = detector.list_models()

        if current_model.model_id not in available_models:

            registry.set_status(
                current_model.model_id,
                LocalLLMStatus.UNAVAILABLE,
            )

            raise RuntimeError(
                f"Local AI model unavailable: "
                f"{current_model.model_id}"
            )

        print(
            "[LOCAL AI] Using selected model: "
            f"{current_model.name}"
        )

        return LocalAIModel.from_llm(
            current_model
        )

    if config.provider == AIProvider.CLOUD:

        if not config.api_key:
            raise ValueError(
                "Cloud AI requires AI_API_KEY"
            )

        if not config.model:
            raise ValueError(
                "Cloud AI requires AI_MODEL"
            )

        if not config.cloud_provider:
            raise ValueError(
                "Cloud AI requires AI_CLOUD_PROVIDER"
            )

        if config.cloud_provider == "openai":

            endpoint = (
                "https://api.openai.com/v1/chat/completions"
            )

            return CloudAIModel(
                api_key=config.api_key,
                endpoint=endpoint,
                model=config.model,
            )

        raise ValueError(
            f"Unsupported cloud provider: "
            f"{config.cloud_provider}"
        )

    raise ValueError(
        f"Unsupported AI provider: "
        f"{config.provider}"
    )
