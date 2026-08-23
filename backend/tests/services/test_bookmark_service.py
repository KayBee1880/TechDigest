from app.extensions import db
from app.models import Article, ArticleSource
from app.services.bookmark_service import BookmarkService
from app.services.user_service import UserService
from app.utils.time import utc_now


def _make_user(email="a@example.com"):
    return UserService().register(email=email, password="password123")


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


def test_add_bookmark_creates_bookmark(app):
    user = _make_user()
    article = _make_article()

    bookmark = BookmarkService().add_bookmark(user_id=user.id, article_id=article.id)

    assert bookmark is not None
    assert bookmark.user_id == user.id
    assert bookmark.article_id == article.id


def test_add_bookmark_is_idempotent(app):
    user = _make_user()
    article = _make_article()
    service = BookmarkService()

    first = service.add_bookmark(user_id=user.id, article_id=article.id)
    second = service.add_bookmark(user_id=user.id, article_id=article.id)

    assert first.id == second.id
    pagination = service.list_bookmarks(user_id=user.id)
    assert pagination.total == 1


def test_add_bookmark_returns_none_for_unknown_article(app):
    user = _make_user()

    result = BookmarkService().add_bookmark(user_id=user.id, article_id=999999)

    assert result is None


def test_update_notes_sets_notes_on_bookmark(app):
    user = _make_user()
    article = _make_article()
    service = BookmarkService()
    bookmark = service.add_bookmark(user_id=user.id, article_id=article.id)

    updated = service.update_notes(
        user_id=user.id, bookmark_id=bookmark.id, notes="Worth revisiting"
    )

    assert updated.notes == "Worth revisiting"


def test_update_notes_returns_none_for_unknown_id(app):
    user = _make_user()

    result = BookmarkService().update_notes(user_id=user.id, bookmark_id=999999, notes="x")

    assert result is None


def test_update_notes_returns_none_for_another_users_bookmark(app):
    owner = _make_user(email="owner@example.com")
    intruder = _make_user(email="intruder@example.com")
    article = _make_article()
    service = BookmarkService()
    bookmark = service.add_bookmark(user_id=owner.id, article_id=article.id)

    result = service.update_notes(user_id=intruder.id, bookmark_id=bookmark.id, notes="x")

    assert result is None


def test_remove_bookmark_removes_and_returns_true(app):
    user = _make_user()
    article = _make_article()
    service = BookmarkService()
    bookmark = service.add_bookmark(user_id=user.id, article_id=article.id)

    removed = service.remove_bookmark(user_id=user.id, bookmark_id=bookmark.id)

    assert removed is True
    assert service.list_bookmarks(user_id=user.id).total == 0


def test_remove_bookmark_returns_false_for_unknown_id(app):
    user = _make_user()

    removed = BookmarkService().remove_bookmark(user_id=user.id, bookmark_id=999999)

    assert removed is False


def test_remove_bookmark_returns_false_for_another_users_bookmark(app):
    owner = _make_user(email="owner@example.com")
    intruder = _make_user(email="intruder@example.com")
    article = _make_article()
    service = BookmarkService()
    bookmark = service.add_bookmark(user_id=owner.id, article_id=article.id)

    removed = service.remove_bookmark(user_id=intruder.id, bookmark_id=bookmark.id)

    assert removed is False
    assert service.list_bookmarks(user_id=owner.id).total == 1


def test_list_bookmarks_returns_only_current_users_bookmarks(app):
    owner = _make_user(email="owner@example.com")
    other = _make_user(email="other@example.com")
    article = _make_article()
    service = BookmarkService()
    service.add_bookmark(user_id=owner.id, article_id=article.id)

    pagination = service.list_bookmarks(user_id=other.id)

    assert pagination.total == 0
