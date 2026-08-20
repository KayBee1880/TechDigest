from unittest.mock import Mock, patch

from app.clients.ollama import OllamaClient


@patch("app.clients.ollama.requests.post")
def test_summarize_returns_stripped_response_text(mock_post):
    mock_post.return_value = Mock(
        json=Mock(return_value={"response": "  A concise summary.  \n"})
    )

    client = OllamaClient(base_url="http://localhost:11434", model="llama3.2")
    result = client.summarize("some article body")

    assert result == "A concise summary."

    called_url, called_kwargs = mock_post.call_args
    assert called_url[0] == "http://localhost:11434/api/generate"
    assert called_kwargs["json"]["model"] == "llama3.2"
    assert "some article body" in called_kwargs["json"]["prompt"]
    assert called_kwargs["json"]["stream"] is False


@patch("app.clients.ollama.requests.post")
def test_summarize_strips_trailing_slash_from_base_url(mock_post):
    mock_post.return_value = Mock(json=Mock(return_value={"response": "ok"}))

    OllamaClient(base_url="http://localhost:11434/", model="llama3.2").summarize("x")

    called_url = mock_post.call_args[0][0]
    assert called_url == "http://localhost:11434/api/generate"
