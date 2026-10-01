import requests

from core.ai.model import AIModel


class CloudAIModel(AIModel):

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        model: str
    ):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model

    def generate(self, prompt: str) -> str:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        response = requests.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]
