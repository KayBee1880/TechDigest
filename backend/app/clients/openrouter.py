import requests

from app.clients.ai_provider import (
    AIProviderClient,
    SummaryResult,
    build_summary_prompt,
    parse_summary_response,
)


class OpenRouterClient(AIProviderClient):
    name = "openrouter"

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def summarize(self, text: str, categories: dict[str, str]) -> SummaryResult:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "user", "content": build_summary_prompt(text, categories)}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0,
            },
            timeout=60,
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()
        return parse_summary_response(raw, categories)
