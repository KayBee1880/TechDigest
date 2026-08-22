from unittest.mock import Mock, patch

from app.clients.base import NormalizedArticle
from app.extensions import db
from app.models import Article, ArticleSource, ProcessingFailure
from app.services.news_ingestion_service import NewsIngestionService
from app.tasks import ingest_all_sources_task, ingest_source_task, summarize_article_task
from app.utils.time import utc_now


def _make_source(name="Test Source", is_active=True):
    source = ArticleSource(
        name=name,
        source_type="rss",
        url="https://example.com/feed",
        is_active=is_active,
    )
    db.session.add(source)
    db.session.commit()
    return source


def _make_article(source, summary_status="pending", raw_content="body"):
    article = Article(
        source_id=source.id,
        title="A Title",
        url="https://example.com/a",
        canonical_url="https://example.com/a",
        title_hash="x" * 64,
        raw_content=raw_content,
        published_at=utc_now(),
        summary_status=summary_status,
    )
    db.session.add(article)
    db.session.commit()
    return article


def _normalized(title, url):
    return NormalizedArticle(
        title=title, url=url, published_at=utc_now(), raw_content="body"
    )


class TestSummarizeArticleTask:
    @patch("app.tasks.SummarizationService")
    def test_success_calls_service_and_records_retry_count(self, mock_service_cls, app):
        source = _make_source()
        article = _make_article(source)
        fake_summary = Mock()
        called_with_id = {}

        def _fake_summarize(passed_article):
            called_with_id["value"] = passed_article.id
            return fake_summary

        mock_service_cls.return_value.summarize.side_effect = _fake_summarize

        summarize_article_task.apply(args=[article.id])

        mock_service_cls.return_value.summarize.assert_called_once()
        assert called_with_id["value"] == article.id
        assert fake_summary.retry_count == 0

    @patch("app.tasks.SummarizationService")
    def test_skips_article_that_is_already_completed(self, mock_service_cls, app):
        source = _make_source()
        article = _make_article(source, summary_status="completed")

        summarize_article_task.apply(args=[article.id])

        mock_service_cls.assert_not_called()

    @patch("app.tasks.SummarizationService")
    def test_marks_unavailable_when_no_raw_content(self, mock_service_cls, app):
        source = _make_source()
        article = _make_article(source, raw_content="")

        summarize_article_task.apply(args=[article.id])

        mock_service_cls.assert_not_called()
        db.session.refresh(article)
        assert article.summary_status == "unavailable"

    @patch("app.tasks.SummarizationService")
    def test_records_failure_and_marks_article_failed_once_retries_exhausted(
        self, mock_service_cls, app
    ):
        source = _make_source()
        article = _make_article(source)
        mock_service_cls.return_value.summarize.side_effect = RuntimeError("boom")

        original_max_retries = summarize_article_task.max_retries
        summarize_article_task.max_retries = 0
        try:
            summarize_article_task.apply(args=[article.id])
        finally:
            summarize_article_task.max_retries = original_max_retries

        db.session.refresh(article)
        assert article.summary_status == "failed"
        failures = ProcessingFailure.query.filter_by(article_id=article.id).all()
        assert len(failures) == 1
        assert failures[0].error_message == "boom"
        assert failures[0].attempt_number == 1


class TestIngestSourceTask:
    @patch("app.tasks.SummarizationService")
    def test_ingests_and_queues_summarization_for_each_new_article(
        self, mock_service_cls, app
    ):
        source = _make_source()
        fake_client = Mock()
        fake_client.fetch.return_value = [_normalized("New", "https://example.com/new")]
        mock_service_cls.return_value.summarize.return_value = Mock()

        with patch.object(NewsIngestionService, "CLIENTS", {"rss": fake_client}):
            ingest_source_task.apply(args=[source.id])

        assert Article.query.count() == 1
        mock_service_cls.return_value.summarize.assert_called_once()

    def test_does_nothing_for_unknown_source_id(self, app):
        ingest_source_task.apply(args=[999999])
        assert Article.query.count() == 0


class TestIngestAllSourcesTask:
    @patch("app.tasks.ingest_source_task.delay")
    def test_queues_ingestion_only_for_active_sources(self, mock_delay, app):
        active = _make_source(name="Active Source", is_active=True)
        _make_source(name="Inactive Source", is_active=False)

        ingest_all_sources_task.apply()

        mock_delay.assert_called_once_with(active.id)
