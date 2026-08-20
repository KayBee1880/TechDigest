import os
from abc import ABC, abstractmethod


class AIProviderClient(ABC):
    name: str

    @abstractmethod
    def summarize(self, text: str) -> str:
        raise NotImplementedError


def get_ai_provider_client() -> AIProviderClient:
    provider = os.environ.get("AI_PROVIDER", "ollama")

    if provider == "ollama":
        from app.clients.ollama import OllamaClient

        return OllamaClient(
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.environ.get("OLLAMA_MODEL", "llama3.2"),
        )

    raise ValueError(f"Unsupported AI_PROVIDER: {provider!r}")
