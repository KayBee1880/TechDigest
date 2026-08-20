import requests

from app.clients.ai_provider import AIProviderClient

SUMMARY_PROMPT = (
    "Summarize the following technology article in 2-3 concise sentences, "
    "covering the concrete news rather than generic commentary:\n\n{content}"
)


class OllamaClient(AIProviderClient):
    name = "ollama"

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def summarize(self, text: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": SUMMARY_PROMPT.format(content=text),
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["response"].strip()
