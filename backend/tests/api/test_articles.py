from app.constants import ARTICLE_CATEGORIES
from app.extensions import db
from app.models import Article, ArticleSource, Summary
from app.utils.time import utc_now


def _make_source(name="Test Source"):
    source = ArticleSource(name=name, source_type="rss", url="https://example.com/feed")
    db.session.add(source)
    db.session.commit()
    return source


def _make_article(source, title="A Title", summary_status="pending", category=None):
    slug = title.lower().replace(" ", "-")
    article = Article(
        source_id=source.id,
        title=title,
        url=f"https://example.com/{slug}",
        canonical_url=f"https://example.com/{slug}",
        title_hash="x" * 64,
        raw_content="body",
        published_at=utc_now(),
        summary_status=summary_status,
        category=category,
    )
    db.session.add(article)
    db.session.commit()
    return article


def test_list_articles_returns_items_with_source_and_summary(app, client):
    source = _make_source(name="Ars Technica")
    article = _make_article(source, summary_status="completed")
    db.session.add(
        Summary(
            article_id=article.id,
            content="A summary.",
            provider="ollama",
            model_name="llama3.2",
        )
    )
    db.session.commit()

    response = client.get("/api/articles")

    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["title"] == "A Title"
    assert item["source"]["name"] == "Ars Technica"
    assert item["summary"]["content"] == "A summary."


def test_list_articles_returns_null_summary_when_pending(app, client):
    source = _make_source()
    _make_article(source, summary_status="pending")

    response = client.get("/api/articles")

    assert response.get_json()["items"][0]["summary"] is None


def test_list_articles_supports_pagination_params(app, client):
    source = _make_source()
    for i in range(3):
        _make_article(source, title=f"Article {i}")

    response = client.get("/api/articles?per_page=2&page=1")

    body = response.get_json()
    assert body["per_page"] == 2
    assert body["total"] == 3
    assert len(body["items"]) == 2


def test_list_articles_filters_by_category(app, client):
    source = _make_source()
    _make_article(source, title="Security Article", category="Security")
    _make_article(source, title="Web Article", category="Web Development")

    response = client.get("/api/articles?category=Security")

    body = response.get_json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Security Article"


def test_list_categories_returns_the_full_taxonomy(app, client):
    response = client.get("/api/articles/categories")

    assert response.status_code == 200
    assert response.get_json() == ARTICLE_CATEGORIES


def test_get_article_detail_returns_article(app, client):
    source = _make_source()
    article = _make_article(source)

    response = client.get(f"/api/articles/{article.id}")

    assert response.status_code == 200
    assert response.get_json()["id"] == article.id


def test_get_article_detail_returns_404_for_missing(app, client):
    response = client.get("/api/articles/999999")

    assert response.status_code == 404
