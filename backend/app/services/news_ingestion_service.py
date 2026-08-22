from collections.abc import Callable

from sqlalchemy.exc import IntegrityError

from app.clients.base import NormalizedArticle
from app.clients.hacker_news import HackerNewsClient
from app.clients.rss_feed import RSSFeedClient
from app.extensions import db
from app.models import Article, ArticleSource, IngestionJob
from app.utils.dedupe import canonicalize_url, hash_title
from app.utils.time import utc_now


class NewsIngestionService:
    CLIENTS = {
        "api": HackerNewsClient(),
        "rss": RSSFeedClient(),
    }

    def ingest(
        self,
        source: ArticleSource,
        on_created: Callable[[Article], None] | None = None,
    ) -> IngestionJob:
        job = IngestionJob(source_id=source.id, status="running")
        db.session.add(job)
        db.session.commit()

        try:
            client = self.CLIENTS[source.source_type]
            raw_articles = client.fetch(source.url)
            job.articles_found = len(raw_articles)

            created_count = 0
            for raw_article in raw_articles:
                article = self._create_article(source, raw_article)
                if article is not None:
                    created_count += 1
                    if on_created is not None:
                        on_created(article)
            job.articles_created = created_count
            job.status = "completed"
        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)
        finally:
            job.finished_at = utc_now()
            db.session.commit()

        return job

    def _create_article(
        self, source: ArticleSource, raw_article: NormalizedArticle
    ) -> Article | None:
        canonical_url = canonicalize_url(raw_article.url)

        if Article.query.filter_by(canonical_url=canonical_url).first() is not None:
            return None

        article = Article(
            source_id=source.id,
            title=raw_article.title,
            url=raw_article.url,
            canonical_url=canonical_url,
            title_hash=hash_title(raw_article.title),
            raw_content=raw_article.raw_content,
            published_at=raw_article.published_at,
        )
        db.session.add(article)

        try:
            db.session.commit()
            return article
        except IntegrityError:
            db.session.rollback()
            return None
