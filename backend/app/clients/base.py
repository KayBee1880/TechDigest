from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

USER_AGENT = "TechDigest/1.0 (+https://github.com/KayBee1880/TechDigest)"


@dataclass
class NormalizedArticle:
    title: str
    url: str
    published_at: datetime
    raw_content: str


class NewsProviderClient(ABC):
    @abstractmethod
    def fetch(self, source_url: str) -> list[NormalizedArticle]:
        raise NotImplementedError
