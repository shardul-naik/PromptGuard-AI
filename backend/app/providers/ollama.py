from typing import Any

import httpx


class OllamaProvider:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
    ) -> None:
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        model: str,
        prompt: str,
    ) -> dict[str, Any]:

        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "stream": False,
                "think": False,
            },
            timeout=120.0,
        )

        response.raise_for_status()

        data = response.json()

        return {
            "response": data["message"]["content"],
        }