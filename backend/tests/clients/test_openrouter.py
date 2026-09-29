import json
from unittest.mock import Mock, patch

import pytest

from app.clients.openrouter import OpenRouterClient

CATEGORIES = {
    "Security": "vulnerabilities, exploits, breaches",
    "Web Development": "browsers, frameworks, web APIs",
    "Other": "anything that does not fit above",
}


@patch("app.clients.openrouter.requests.post")
def test_summarize_returns_parsed_summary_and_category(mock_post):
    mock_post.return_value = Mock(
        json=Mock(
            return_value={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {"summary": "  A concise summary.  \n", "category": "Security"}
                            )
                        }
                    }
                ]
            }
        )
    )

    client = OpenRouterClient(api_key="test-key", model="test-vendor/test-model:free")
    result = client.summarize("some article body", CATEGORIES)

    assert result.summary == "A concise summary."
    assert result.category == "Security"

    called_url, called_kwargs = mock_post.call_args
    assert called_url[0] == "https://openrouter.ai/api/v1/chat/completions"
    assert called_kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert called_kwargs["json"]["model"] == "test-vendor/test-model:free"
    assert "some article body" in called_kwargs["json"]["messages"][0]["content"]
    assert "Security: vulnerabilities, exploits, breaches" in (
        called_kwargs["json"]["messages"][0]["content"]
    )
    assert called_kwargs["json"]["response_format"] == {"type": "json_object"}
    assert called_kwargs["json"]["temperature"] == 0


@patch("app.clients.openrouter.requests.post")
def test_summarize_raises_descriptive_error_when_http_200_carries_an_error_body(mock_post):
    mock_post.return_value = Mock(
        json=Mock(
            return_value={
                "error": {"message": "Upstream error: Service temporarily overloaded", "code": 503}
            }
        )
    )

    client = OpenRouterClient(api_key="test-key", model="some-model")

    with pytest.raises(RuntimeError, match="503.*temporarily overloaded"):
        client.summarize("x", CATEGORIES)


@patch("app.clients.openrouter.requests.post")
def test_summarize_falls_back_to_other_for_unrecognized_category(mock_post):
    mock_post.return_value = Mock(
        json=Mock(
            return_value={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {"summary": "A summary.", "category": "Not A Real One"}
                            )
                        }
                    }
                ]
            }
        )
    )

    client = OpenRouterClient(api_key="test-key", model="some-model")
    result = client.summarize("x", CATEGORIES)

    assert result.category == "Other"


@patch("app.clients.openrouter.requests.post")
def test_summarize_falls_back_when_response_is_not_valid_json(mock_post):
    mock_post.return_value = Mock(
        json=Mock(
            return_value={
                "choices": [{"message": {"content": "Not JSON at all, just plain text."}}]
            }
        )
    )

    client = OpenRouterClient(api_key="test-key", model="some-model")
    result = client.summarize("x", CATEGORIES)

    assert result.summary == "Not JSON at all, just plain text."
    assert result.category == "Other"
