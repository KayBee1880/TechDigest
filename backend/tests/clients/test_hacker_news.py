from unittest.mock import Mock, patch

from app.clients.hacker_news import HackerNewsClient


def _response(json_data):
    return Mock(json=Mock(return_value=json_data))


@patch("app.clients.hacker_news.requests.get")
def test_fetch_combines_story_list_and_item_details(mock_get):
    mock_get.side_effect = [
        _response([1, 2]),
        _response({"title": "Story One", "url": "https://example.com/one", "time": 1704110400}),
        _response({"title": "Ask HN: Something", "time": 1704110400, "text": "<p>body</p>"}),
    ]

    articles = HackerNewsClient(limit=2).fetch("https://hn.example/topstories.json")

    assert len(articles) == 2
    assert articles[0].url == "https://example.com/one"
    assert articles[1].url == "https://news.ycombinator.com/item?id=2"
    assert articles[1].raw_content == "<p>body</p>"


@patch("app.clients.hacker_news.requests.get")
def test_fetch_respects_limit(mock_get):
    mock_get.side_effect = [_response(list(range(1, 501)))] + [
        _response({"title": "Story", "time": 0}) for _ in range(5)
    ]

    articles = HackerNewsClient(limit=5).fetch("https://hn.example/topstories.json")

    assert len(articles) == 5


@patch("app.clients.hacker_news.requests.get")
def test_fetch_skips_deleted_items(mock_get):
    mock_get.side_effect = [
        _response([1, 2]),
        _response(None),
        _response({"title": "Real", "time": 0, "url": "https://example.com/real"}),
    ]

    articles = HackerNewsClient(limit=2).fetch("https://hn.example/topstories.json")

    assert len(articles) == 1
    assert articles[0].title == "Real"
