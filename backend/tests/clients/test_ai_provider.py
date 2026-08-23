import pytest

from app.clients.ai_provider import (
    build_summary_prompt,
    get_ai_provider_client,
    parse_summary_response,
)
from app.clients.ollama import OllamaClient
from app.clients.openrouter import OpenRouterClient

CATEGORIES = {
    "Security": "vulnerabilities, exploits, breaches",
    "Other": "anything that does not fit above",
}


def test_build_summary_prompt_includes_content_and_category_descriptions():
    prompt = build_summary_prompt("some article text", CATEGORIES)

    assert "some article text" in prompt
    assert "Security: vulnerabilities, exploits, breaches" in prompt


def test_parse_summary_response_parses_valid_json():
    result = parse_summary_response('{"summary": "s", "category": "Security"}', CATEGORIES)

    assert result.summary == "s"
    assert result.category == "Security"


def test_parse_summary_response_falls_back_to_other_for_unrecognized_category():
    result = parse_summary_response('{"summary": "s", "category": "Nope"}', CATEGORIES)

    assert result.category == "Other"


def test_parse_summary_response_falls_back_when_not_valid_json():
    result = parse_summary_response("plain text response", CATEGORIES)

    assert result.summary == "plain text response"
    assert result.category == "Other"


def test_get_ai_provider_client_defaults_to_ollama(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)

    client = get_ai_provider_client()

    assert isinstance(client, OllamaClient)


def test_get_ai_provider_client_returns_openrouter_client(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    client = get_ai_provider_client()

    assert isinstance(client, OpenRouterClient)
    assert client.api_key == "test-key"


def test_get_ai_provider_client_raises_for_missing_openrouter_key(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openrouter")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(KeyError):
        get_ai_provider_client()


def test_get_ai_provider_client_raises_for_unsupported_provider(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "not-a-real-provider")

    with pytest.raises(ValueError):
        get_ai_provider_client()
