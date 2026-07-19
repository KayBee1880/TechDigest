from datetime import datetime

import requests

from app.clients.base import USER_AGENT, NewsProviderClient, NormalizedArticle

ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"


class HackerNewsClient(NewsProviderClient):
    def __init__(self, limit: int = 30):
        self.limit = limit

    def fetch(self, source_url: str) -> list[NormalizedArticle]:
        response = requests.get(
            source_url, headers={"User-Agent": USER_AGENT}, timeout=10
        )
        response.raise_for_status()
        story_ids = response.json()[: self.limit]

        articles = []
        for story_id in story_ids:
            item = self._fetch_item(story_id)
            if item is None:
                continue
            articles.append(self._to_normalized_article(story_id, item))
        return articles

    @staticmethod
    def _fetch_item(story_id: int) -> dict | None:
        response = requests.get(
            ITEM_URL.format(item_id=story_id),
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _to_normalized_article(story_id: int, item: dict) -> NormalizedArticle:
        discussion_url = f"https://news.ycombinator.com/item?id={story_id}"
        return NormalizedArticle(
            title=item.get("title", ""),
            url=item.get("url", discussion_url),
            published_at=datetime.utcfromtimestamp(item.get("time", 0)),
            raw_content=item.get("text", ""),
        )
