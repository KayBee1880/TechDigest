import json

import requests

from app.clients.ai_provider import AIProviderClient, SummaryResult

SUMMARY_PROMPT = (
    "Analyze the following technology article. Respond with ONLY a JSON object "
    'with two keys: "summary" (2-3 concise sentences covering the concrete news, '
    'not generic commentary) and "category" (choose the single best match from '
    "this list, using the exact name):\n{categories}\n\nArticle:\n{content}"
)


class OllamaClient(AIProviderClient):
    name = "ollama"

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def summarize(self, text: str, categories: dict[str, str]) -> SummaryResult:
        categories_text = "\n".join(f"- {name}: {desc}" for name, desc in categories.items())

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": SUMMARY_PROMPT.format(categories=categories_text, content=text),
                "format": "json",
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=60,
        )
        response.raise_for_status()
        raw = response.json()["response"].strip()

        try:
            parsed = json.loads(raw)
            summary = str(parsed["summary"]).strip()
            category = str(parsed.get("category", "")).strip()
        except (json.JSONDecodeError, KeyError, TypeError):
            summary = raw
            category = ""

        if category not in categories:
            category = "Other"

        return SummaryResult(summary=summary, category=category)
