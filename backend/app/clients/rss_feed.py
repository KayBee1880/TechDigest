from datetime import datetime

import feedparser
import requests

from app.clients.base import USER_AGENT, NewsProviderClient, NormalizedArticle


class RSSFeedClient(NewsProviderClient):
    def fetch(self, source_url: str) -> list[NormalizedArticle]:
        response = requests.get(
            source_url, headers={"User-Agent": USER_AGENT}, timeout=10
        )
        response.raise_for_status()

        parsed = feedparser.parse(response.content)

        return [
            NormalizedArticle(
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                published_at=self._parse_published(entry),
                raw_content=entry.get("summary", ""),
            )
            for entry in parsed.entries
        ]

    @staticmethod
    def _parse_published(entry) -> datetime:
        if entry.get("published_parsed"):
            return datetime(*entry.published_parsed[:6])
        return datetime.utcnow()
