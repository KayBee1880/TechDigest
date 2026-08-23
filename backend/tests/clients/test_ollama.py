import json
from unittest.mock import Mock, patch

from app.clients.ollama import OllamaClient

CATEGORIES = {
    "Security": "vulnerabilities, exploits, breaches",
    "Web Development": "browsers, frameworks, web APIs",
    "Other": "anything that does not fit above",
}


@patch("app.clients.ollama.requests.post")
def test_summarize_returns_parsed_summary_and_category(mock_post):
    mock_post.return_value = Mock(
        json=Mock(
            return_value={
                "response": json.dumps(
                    {"summary": "  A concise summary.  \n", "category": "Security"}
                )
            }
        )
    )

    client = OllamaClient(base_url="http://localhost:11434", model="llama3.2")
    result = client.summarize("some article body", CATEGORIES)

    assert result.summary == "A concise summary."
    assert result.category == "Security"

    called_url, called_kwargs = mock_post.call_args
    assert called_url[0] == "http://localhost:11434/api/generate"
    assert called_kwargs["json"]["model"] == "llama3.2"
    assert "some article body" in called_kwargs["json"]["prompt"]
    assert "Security: vulnerabilities, exploits, breaches" in called_kwargs["json"]["prompt"]
    assert called_kwargs["json"]["format"] == "json"
    assert called_kwargs["json"]["options"] == {"temperature": 0}
    assert called_kwargs["json"]["stream"] is False


@patch("app.clients.ollama.requests.post")
def test_summarize_strips_trailing_slash_from_base_url(mock_post):
    mock_post.return_value = Mock(
        json=Mock(
            return_value={"response": json.dumps({"summary": "ok", "category": "Other"})}
        )
    )

    OllamaClient(base_url="http://localhost:11434/", model="llama3.2").summarize(
        "x", CATEGORIES
    )

    called_url = mock_post.call_args[0][0]
    assert called_url == "http://localhost:11434/api/generate"


@patch("app.clients.ollama.requests.post")
def test_summarize_falls_back_to_other_for_unrecognized_category(mock_post):
    mock_post.return_value = Mock(
        json=Mock(
            return_value={
                "response": json.dumps({"summary": "A summary.", "category": "Not A Real One"})
            }
        )
    )

    client = OllamaClient(base_url="http://localhost:11434", model="llama3.2")
    result = client.summarize("x", CATEGORIES)

    assert result.category == "Other"


@patch("app.clients.ollama.requests.post")
def test_summarize_falls_back_when_response_is_not_valid_json(mock_post):
    mock_post.return_value = Mock(
        json=Mock(return_value={"response": "Not JSON at all, just plain text."})
    )

    client = OllamaClient(base_url="http://localhost:11434", model="llama3.2")
    result = client.summarize("x", CATEGORIES)

    assert result.summary == "Not JSON at all, just plain text."
    assert result.category == "Other"
