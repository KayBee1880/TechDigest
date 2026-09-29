import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

SUMMARY_PROMPT = (
    "Analyze the following technology article. Respond with ONLY a JSON object "
    'with two keys: "summary" (2-3 concise sentences covering the concrete news, '
    'not generic commentary) and "category" (choose the single best match from '
    "this list, using the exact name):\n{categories}\n\nArticle:\n{content}"
)


@dataclass
class SummaryResult:
    summary: str
    category: str


class AIProviderClient(ABC):
    name: str

    @abstractmethod
    def summarize(self, text: str, categories: dict[str, str]) -> SummaryResult:
        raise NotImplementedError


def build_summary_prompt(text: str, categories: dict[str, str]) -> str:
    categories_text = "\n".join(f"- {name}: {desc}" for name, desc in categories.items())
    return SUMMARY_PROMPT.format(categories=categories_text, content=text)


def parse_summary_response(raw: str, categories: dict[str, str]) -> SummaryResult:
    try:
        parsed = json.loads(raw)
        summary = str(parsed["summary"]).strip()
        category = str(parsed.get("category", "")).strip()
    except (json.JSONDecodeError, KeyError, TypeError):
        summary = raw.strip()
        category = ""

    if category not in categories:
        category = "Other"

    return SummaryResult(summary=summary, category=category)


def get_ai_provider_client() -> AIProviderClient:
    provider = os.environ.get("AI_PROVIDER", "ollama")

    if provider == "ollama":
        from app.clients.ollama import OllamaClient

        return OllamaClient(
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.environ.get("OLLAMA_MODEL", "llama3.2"),
        )

    if provider == "openrouter":
        from app.clients.openrouter import OpenRouterClient

        return OpenRouterClient(
            api_key=os.environ["OPENROUTER_API_KEY"],
            model=os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free"),
        )

    raise ValueError(f"Unsupported AI_PROVIDER: {provider!r}")
