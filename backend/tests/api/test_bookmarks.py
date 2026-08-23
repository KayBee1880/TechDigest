from app.extensions import db
from app.models import Article, ArticleSource
from app.services.user_service import UserService
from app.utils.time import utc_now


def _make_user(email="a@example.com"):
    return UserService().register(email=email, password="password123")


def _auth_headers(user):
    return {"Authorization": f"Bearer {UserService().generate_token(user)}"}


def _make_article(title="A Title"):
    source = ArticleSource(name="Test Source", source_type="rss", url="https://example.com/feed")
    db.session.add(source)
    db.session.commit()

    slug = title.lower().replace(" ", "-")
    article = Article(
        source_id=source.id,
        title=title,
        url=f"https://example.com/{slug}",
        canonical_url=f"https://example.com/{slug}",
        title_hash="x" * 64,
        raw_content="body",
        published_at=utc_now(),
    )
    db.session.add(article)
    db.session.commit()
    return article


def test_list_bookmarks_requires_auth(app, client):
    response = client.get("/api/bookmarks")

    assert response.status_code == 401


def test_create_bookmark_returns_201(app, client):
    user = _make_user()
    article = _make_article()

    response = client.post(
        "/api/bookmarks",
        json={"article_id": article.id},
        headers=_auth_headers(user),
    )

    assert response.status_code == 201
    assert response.get_json()["article"]["id"] == article.id


def test_create_bookmark_returns_404_for_unknown_article(app, client):
    user = _make_user()

    response = client.post(
        "/api/bookmarks", json={"article_id": 999999}, headers=_auth_headers(user)
    )

    assert response.status_code == 404


def test_list_bookmarks_returns_only_current_users_bookmarks(app, client):
    owner = _make_user(email="owner@example.com")
    other = _make_user(email="other@example.com")
    article = _make_article()
    client.post(
        "/api/bookmarks", json={"article_id": article.id}, headers=_auth_headers(owner)
    )

    response = client.get("/api/bookmarks", headers=_auth_headers(other))

    assert response.get_json()["total"] == 0


def test_update_bookmark_sets_notes(app, client):
    user = _make_user()
    article = _make_article()
    create_response = client.post(
        "/api/bookmarks", json={"article_id": article.id}, headers=_auth_headers(user)
    )
    bookmark_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/bookmarks/{bookmark_id}",
        json={"notes": "Worth revisiting"},
        headers=_auth_headers(user),
    )

    assert response.status_code == 200
    assert response.get_json()["notes"] == "Worth revisiting"


def test_update_bookmark_returns_404_for_another_users_bookmark(app, client):
    owner = _make_user(email="owner@example.com")
    intruder = _make_user(email="intruder@example.com")
    article = _make_article()
    create_response = client.post(
        "/api/bookmarks", json={"article_id": article.id}, headers=_auth_headers(owner)
    )
    bookmark_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/bookmarks/{bookmark_id}",
        json={"notes": "x"},
        headers=_auth_headers(intruder),
    )

    assert response.status_code == 404


def test_delete_bookmark_returns_204(app, client):
    user = _make_user()
    article = _make_article()
    create_response = client.post(
        "/api/bookmarks", json={"article_id": article.id}, headers=_auth_headers(user)
    )
    bookmark_id = create_response.get_json()["id"]

    response = client.delete(f"/api/bookmarks/{bookmark_id}", headers=_auth_headers(user))

    assert response.status_code == 204


def test_delete_bookmark_returns_404_for_another_users_bookmark(app, client):
    owner = _make_user(email="owner@example.com")
    intruder = _make_user(email="intruder@example.com")
    article = _make_article()
    create_response = client.post(
        "/api/bookmarks", json={"article_id": article.id}, headers=_auth_headers(owner)
    )
    bookmark_id = create_response.get_json()["id"]

    response = client.delete(
        f"/api/bookmarks/{bookmark_id}", headers=_auth_headers(intruder)
    )

    assert response.status_code == 404
