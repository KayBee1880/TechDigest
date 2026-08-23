import requests

from app.clients.ai_provider import (
    AIProviderClient,
    SummaryResult,
    build_summary_prompt,
    parse_summary_response,
)


class OllamaClient(AIProviderClient):
    name = "ollama"

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def summarize(self, text: str, categories: dict[str, str]) -> SummaryResult:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": build_summary_prompt(text, categories),
                "format": "json",
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=60,
        )
        response.raise_for_status()
        raw = response.json()["response"].strip()
        return parse_summary_response(raw, categories)
