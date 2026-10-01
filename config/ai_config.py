import os

from dotenv import load_dotenv
from enum import Enum
from pydantic import BaseModel


load_dotenv()


class AIProvider(str, Enum):
    TEST = "test"
    LOCAL = "local"
    CLOUD = "cloud"


class AIConfig(BaseModel):

    provider: AIProvider = AIProvider.TEST

    cloud_provider: str | None = None
    api_key: str | None = None
    model: str | None = None

    local_runtime: str = "ollama"
    local_endpoint: str = "http://localhost:11434"
    local_model: str | None = None

    @classmethod
    def from_environment(cls):

        return cls(
            provider=os.getenv(
                "AI_PROVIDER",
                "test"
            ),

            cloud_provider=os.getenv(
                "AI_CLOUD_PROVIDER"
            ),

            api_key=os.getenv(
                "AI_API_KEY"
            ),

            model=os.getenv(
                "AI_MODEL"
            ),

            local_runtime=os.getenv(
                "AI_LOCAL_RUNTIME",
                "ollama"
            ),

            local_endpoint=os.getenv(
                "AI_LOCAL_ENDPOINT",
                "http://localhost:11434"
            ),

            local_model=os.getenv(
                "AI_LOCAL_MODEL"
            ),
        )
