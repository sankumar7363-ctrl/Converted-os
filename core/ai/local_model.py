import requests

from core.ai.model import AIModel
from core.ai.local_registry import LocalLLM


class LocalAIModel(AIModel):

    def __init__(
        self,
        endpoint: str,
        model: str,
        runtime: str = "ollama"
    ):
        self.endpoint = endpoint
        self.model = model
        self.runtime = runtime

    @classmethod
    def from_llm(
        cls,
        llm: LocalLLM
    ):

        return cls(
            endpoint=llm.endpoint,
            model=llm.model_id,
            runtime=llm.runtime,
        )

    def generate(
        self,
        prompt: str
    ) -> str:

        if self.runtime != "ollama":
            raise ValueError(
                f"Unsupported local runtime: "
                f"{self.runtime}"
            )

        endpoint = (
            f"{self.endpoint.rstrip('/')}"
            "/api/generate"
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        response = requests.post(
            endpoint,
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]
