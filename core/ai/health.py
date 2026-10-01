from config.ai_config import AIConfig, AIProvider

from core.ai.provider import create_ai_model
from core.ai.provider_result import AIProviderResult
from core.ai.status import AIAvailability


class AIHealthChecker:

    def check(
        self,
        config: AIConfig,
    ) -> AIProviderResult:

        try:

            model = create_ai_model(config)

            return AIProviderResult(
                status=AIAvailability.AVAILABLE,
                model=model,
                message="AI provider is available",
            )

        except ValueError as error:

            message = str(error)

            if (
                config.provider == AIProvider.LOCAL
                and "No installed local AI model" in message
            ):

                return AIProviderResult(
                    status=AIAvailability.NOT_CONFIGURED,
                    message=message,
                )

            return AIProviderResult(
                status=AIAvailability.ERROR,
                message=message,
            )

        except RuntimeError as error:

            return AIProviderResult(
                status=AIAvailability.UNAVAILABLE,
                message=str(error),
            )

        except Exception as error:

            return AIProviderResult(
                status=AIAvailability.ERROR,
                message=str(error),
            )
