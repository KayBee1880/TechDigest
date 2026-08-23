from unittest.mock import Mock

from app.clients.ai_provider import SummaryResult
from app.constants import ARTICLE_CATEGORY_DESCRIPTIONS
from app.extensions import db
from app.models import Article, ArticleSource, Summary
from app.services.summarization_service import SummarizationService
from app.utils.time import utc_now


def _make_article(raw_content="Full article body."):
    source = ArticleSource(
        name="Test Source", source_type="rss", url="https://example.com/feed"
    )
    db.session.add(source)
    db.session.commit()

    article = Article(
        source_id=source.id,
        title="A Title",
        url="https://example.com/a",
        canonical_url="https://example.com/a",
        title_hash="x" * 64,
        raw_content=raw_content,
        published_at=utc_now(),
    )
    db.session.add(article)
    db.session.commit()
    return article


def _fake_client(summary_text="A generated summary.", category="Security"):
    client = Mock()
    client.name = "ollama"
    client.model = "llama3.2"
    client.summarize.return_value = SummaryResult(summary=summary_text, category=category)
    return client


def test_summarize_creates_summary_and_marks_article_completed(app):
    article = _make_article()
    client = _fake_client("A generated summary.", category="Security")

    summary = SummarizationService(client=client).summarize(article)

    client.summarize.assert_called_once_with(article.raw_content, ARTICLE_CATEGORY_DESCRIPTIONS)
    assert summary.content == "A generated summary."
    assert summary.provider == "ollama"
    assert summary.model_name == "llama3.2"
    assert article.category == "Security"
    assert article.summary_status == "completed"
    assert Summary.query.filter_by(article_id=article.id).count() == 1


def test_summarize_falls_back_to_title_when_no_raw_content(app):
    article = _make_article(raw_content="")
    client = _fake_client()

    SummarizationService(client=client).summarize(article)

    client.summarize.assert_called_once_with(article.title, ARTICLE_CATEGORY_DESCRIPTIONS)


def test_summarize_updates_existing_summary_instead_of_duplicating(app):
    article = _make_article()
    db.session.add(
        Summary(
            article_id=article.id,
            content="stale",
            provider="ollama",
            model_name="llama3.2",
        )
    )
    db.session.commit()

    client = _fake_client("Fresh summary.")
    SummarizationService(client=client).summarize(article)

    assert Summary.query.filter_by(article_id=article.id).count() == 1
    assert Summary.query.filter_by(article_id=article.id).first().content == (
        "Fresh summary."
    )
