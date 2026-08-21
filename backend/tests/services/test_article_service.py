from datetime import timedelta

from app.extensions import db
from app.models import Article, ArticleSource
from app.services.article_service import ArticleService
from app.utils.time import utc_now


def _make_source(name="Test Source"):
    source = ArticleSource(name=name, source_type="rss", url="https://example.com/feed")
    db.session.add(source)
    db.session.commit()
    return source


def _make_article(source, title="A Title", published_at=None):
    article = Article(
        source_id=source.id,
        title=title,
        url=f"https://example.com/{title.lower().replace(' ', '-')}",
        canonical_url=f"https://example.com/{title.lower().replace(' ', '-')}",
        title_hash="x" * 64,
        raw_content="body",
        published_at=published_at or utc_now(),
    )
    db.session.add(article)
    db.session.commit()
    return article


def test_list_articles_returns_paginated_results(app):
    source = _make_source()
    for i in range(3):
        _make_article(source, title=f"Article {i}")

    pagination = ArticleService().list_articles(page=1, per_page=2)

    assert pagination.total == 3
    assert len(pagination.items) == 2


def test_list_articles_orders_newest_first(app):
    source = _make_source()
    older = _make_article(source, title="Older", published_at=utc_now() - timedelta(days=1))
    newer = _make_article(source, title="Newer", published_at=utc_now())

    pagination = ArticleService().list_articles()

    assert [a.id for a in pagination.items] == [newer.id, older.id]


def test_list_articles_filters_by_source_id(app):
    source_a = _make_source(name="Source A")
    source_b = _make_source(name="Source B")
    article_a = _make_article(source_a, title="From A")
    _make_article(source_b, title="From B")

    pagination = ArticleService().list_articles(source_id=source_a.id)

    assert [a.id for a in pagination.items] == [article_a.id]


def test_list_articles_filters_by_search_query(app):
    source = _make_source()
    match = _make_article(source, title="Python 3.14 released")
    _make_article(source, title="Something unrelated")

    pagination = ArticleService().list_articles(q="python")

    assert [a.id for a in pagination.items] == [match.id]


def test_list_articles_caps_per_page_at_max(app):
    source = _make_source()
    _make_article(source, title="Only Article")

    pagination = ArticleService().list_articles(per_page=1000)

    assert pagination.per_page == ArticleService.MAX_PER_PAGE


def test_get_article_returns_article(app):
    source = _make_source()
    article = _make_article(source)

    result = ArticleService().get_article(article.id)

    assert result.id == article.id


def test_get_article_returns_none_for_unknown_id(app):
    result = ArticleService().get_article(999999)

    assert result is None
