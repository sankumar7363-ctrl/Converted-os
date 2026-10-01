import requests


class OllamaDetector:

    def __init__(
        self,
        endpoint: str = "http://localhost:11434"
    ):
        self.endpoint = endpoint.rstrip("/")

    def is_available(self) -> bool:

        try:

            response = requests.get(
                self.endpoint,
                timeout=5,
            )

            return response.status_code == 200

        except requests.RequestException:

            return False

    def list_models(self) -> list[str]:

        if not self.is_available():

            return []

        try:

            response = requests.get(
                f"{self.endpoint}/api/tags",
                timeout=5,
            )

            response.raise_for_status()

            data = response.json()

            return [
                model["name"]
                for model in data.get(
                    "models",
                    []
                )
            ]

        except (
            requests.RequestException,
            ValueError,
            KeyError,
        ):

            return []


class LocalRuntimeDetector:

    def __init__(
        self,
        runtime: str,
        endpoint: str
    ):

        self.runtime = runtime
        self.endpoint = endpoint

    def is_available(self) -> bool:

        if self.runtime == "ollama":

            detector = OllamaDetector(
                self.endpoint
            )

            return detector.is_available()

        return False

    def list_models(self) -> list[str]:

        if self.runtime == "ollama":

            detector = OllamaDetector(
                self.endpoint
            )

            return detector.list_models()

        return []
