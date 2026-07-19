from unittest.mock import Mock, patch

from app.clients.base import NormalizedArticle
from app.extensions import db
from app.models import Article, ArticleSource
from app.services.news_ingestion_service import NewsIngestionService
from app.utils.time import utc_now


def _normalized(title, url):
    return NormalizedArticle(
        title=title, url=url, published_at=utc_now(), raw_content="body"
    )


def _make_source():
    source = ArticleSource(
        name="Test Source", source_type="rss", url="https://example.com/feed"
    )
    db.session.add(source)
    db.session.commit()
    return source


def test_ingest_creates_new_articles(app):
    source = _make_source()
    fake_client = Mock()
    fake_client.fetch.return_value = [
        _normalized("First", "https://example.com/first"),
        _normalized("Second", "https://example.com/second"),
    ]

    with patch.object(NewsIngestionService, "CLIENTS", {"rss": fake_client}):
        job = NewsIngestionService().ingest(source)

    assert job.status == "completed"
    assert job.articles_found == 2
    assert job.articles_created == 2
    assert Article.query.count() == 2


def test_ingest_skips_existing_duplicates(app):
    source = _make_source()
    db.session.add(
        Article(
            source_id=source.id,
            title="First",
            url="https://example.com/first",
            canonical_url="https://example.com/first",
            title_hash="x" * 64,
            raw_content="",
            published_at=utc_now(),
        )
    )
    db.session.commit()

    fake_client = Mock()
    fake_client.fetch.return_value = [
        _normalized("First", "https://example.com/first"),
        _normalized("Second", "https://example.com/second"),
    ]

    with patch.object(NewsIngestionService, "CLIENTS", {"rss": fake_client}):
        job = NewsIngestionService().ingest(source)

    assert job.articles_found == 2
    assert job.articles_created == 1
    assert Article.query.count() == 2


def test_ingest_records_failure_when_client_raises(app):
    source = _make_source()
    fake_client = Mock()
    fake_client.fetch.side_effect = RuntimeError("feed unreachable")

    with patch.object(NewsIngestionService, "CLIENTS", {"rss": fake_client}):
        job = NewsIngestionService().ingest(source)

    assert job.status == "failed"
    assert job.error_message == "feed unreachable"
    assert Article.query.count() == 0
