from unittest.mock import Mock, patch

import pytest
import requests

from app.clients.rss_feed import RSSFeedClient

SAMPLE_FEED = b"""<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>Sample Feed</title>
    <item>
      <title>First Article</title>
      <link>https://example.com/first</link>
      <description>Summary of the first article</description>
      <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""


@patch("app.clients.rss_feed.requests.get")
def test_fetch_returns_normalized_articles(mock_get):
    mock_get.return_value = Mock(content=SAMPLE_FEED)

    articles = RSSFeedClient().fetch("https://example.com/feed")

    assert len(articles) == 1
    assert articles[0].title == "First Article"
    assert articles[0].url == "https://example.com/first"
    assert articles[0].raw_content == "Summary of the first article"


@patch("app.clients.rss_feed.requests.get")
def test_fetch_sends_timeout_and_user_agent(mock_get):
    mock_get.return_value = Mock(content=SAMPLE_FEED)

    RSSFeedClient().fetch("https://example.com/feed")

    _, kwargs = mock_get.call_args
    assert kwargs["timeout"] == 10
    assert "User-Agent" in kwargs["headers"]


@patch("app.clients.rss_feed.requests.get")
def test_fetch_raises_on_http_error(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404")
    mock_get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        RSSFeedClient().fetch("https://example.com/feed")
