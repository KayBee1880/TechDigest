from datetime import timedelta
from unittest.mock import patch

import pytest

from app.extensions import db
from app.models import Article, ArticleSource, ProcessingFailure
from app.utils.time import utc_now
from scripts import run_production_pipeline as pipeline


@pytest.fixture(autouse=True)
def mock_ingestion():
    # Sources default to is_active=True, so without this run_pipeline() would really call
    # the RSS client for every fixture source. Ingestion has its own tests; patching it here
    # keeps this file at zero live network calls like the rest of the suite.
    with patch("scripts.run_production_pipeline.NewsIngestionService") as mock_cls:
        yield mock_cls.return_value


def _make_source(name="Test Source", is_active=True):
    source = ArticleSource(
        name=name, source_type="rss", url=f"https://example.com/{name}", is_active=is_active
    )
    db.session.add(source)
    db.session.commit()
    return source


def _make_article(source, slug, raw_content="body", age_days=0, summary_status="pending"):
    article = Article(
        source_id=source.id,
        title=slug,
        url=f"https://example.com/{slug}",
        canonical_url=f"https://example.com/{slug}",
        title_hash="x" * 64,
        raw_content=raw_content,
        published_at=utc_now() - timedelta(days=age_days),
        summary_status=summary_status,
    )
    db.session.add(article)
    db.session.commit()
    return article


def test_run_pipeline_ingests_only_active_sources(mock_ingestion, app):
    active = _make_source("active")
    _make_source("inactive", is_active=False)

    pipeline.run_pipeline()

    assert [c.args[0].id for c in mock_ingestion.ingest.call_args_list] == [active.id]


@patch("scripts.run_production_pipeline.SummarizationService")
def test_run_pipeline_counts_successful_summaries(mock_service_cls, app):
    source = _make_source()
    _make_article(source, "a")
    _make_article(source, "b")

    attempted, succeeded = pipeline.run_pipeline()

    assert (attempted, succeeded) == (2, 2)
    assert mock_service_cls.return_value.summarize.call_count == 2


@patch("scripts.run_production_pipeline.SummarizationService")
def test_run_pipeline_marks_content_less_articles_unavailable_without_an_ai_call(
    mock_service_cls, app
):
    source = _make_source()
    empty = _make_article(source, "empty", raw_content="")
    real = _make_article(source, "real")

    attempted, succeeded = pipeline.run_pipeline()

    assert (attempted, succeeded) == (1, 1)
    db.session.refresh(empty)
    assert empty.summary_status == "unavailable"
    mock_service_cls.return_value.summarize.assert_called_once()
    assert mock_service_cls.return_value.summarize.call_args[0][0].id == real.id


@patch("scripts.run_production_pipeline.MAX_SUMMARIES_PER_RUN", 2)
@patch("scripts.run_production_pipeline.SummarizationService")
def test_run_pipeline_caps_attempts_per_run_and_takes_newest_first(mock_service_cls, app):
    source = _make_source()
    _make_article(source, "oldest", age_days=3)
    newest = _make_article(source, "newest", age_days=0)
    middle = _make_article(source, "middle", age_days=1)
    summarized = []
    mock_service_cls.return_value.summarize.side_effect = lambda a: summarized.append(a.id)

    attempted, _ = pipeline.run_pipeline()

    assert attempted == 2
    assert summarized == [newest.id, middle.id]


@patch("scripts.run_production_pipeline.SummarizationService")
def test_failed_attempt_is_logged_and_article_stays_pending_for_the_next_run(
    mock_service_cls, app
):
    source = _make_source()
    article = _make_article(source, "a")
    mock_service_cls.return_value.summarize.side_effect = RuntimeError("upstream down")

    attempted, succeeded = pipeline.run_pipeline()

    assert (attempted, succeeded) == (1, 0)
    db.session.refresh(article)
    assert article.summary_status == "pending"
    failure = ProcessingFailure.query.filter_by(article_id=article.id).one()
    assert failure.attempt_number == 1
    assert "upstream down" in failure.error_message


@patch("scripts.run_production_pipeline.SummarizationService")
def test_article_is_marked_failed_once_attempts_are_exhausted(mock_service_cls, app):
    source = _make_source()
    article = _make_article(source, "a")
    for n in range(1, pipeline.MAX_ATTEMPTS):
        db.session.add(
            ProcessingFailure(article_id=article.id, attempt_number=n, error_message="x")
        )
    db.session.commit()
    mock_service_cls.return_value.summarize.side_effect = RuntimeError("still down")

    pipeline.run_pipeline()

    db.session.refresh(article)
    assert article.summary_status == "failed"


def test_exit_code_fails_the_job_only_when_work_was_attempted_and_none_succeeded():
    assert pipeline.exit_code(attempted=5, succeeded=0) == 1
    assert pipeline.exit_code(attempted=5, succeeded=1) == 0
    assert pipeline.exit_code(attempted=0, succeeded=0) == 0
