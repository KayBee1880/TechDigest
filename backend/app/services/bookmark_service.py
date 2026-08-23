from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Article, Bookmark


class BookmarkService:
    DEFAULT_PER_PAGE = 20
    MAX_PER_PAGE = 100

    def list_bookmarks(self, user_id: int, page: int = 1, per_page: int = DEFAULT_PER_PAGE):
        per_page = min(per_page, self.MAX_PER_PAGE)
        query = (
            Bookmark.query.filter_by(user_id=user_id)
            .order_by(Bookmark.created_at.desc())
        )
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def add_bookmark(self, user_id: int, article_id: int) -> Bookmark | None:
        if db.session.get(Article, article_id) is None:
            return None

        existing = Bookmark.query.filter_by(
            user_id=user_id, article_id=article_id
        ).first()
        if existing is not None:
            return existing

        bookmark = Bookmark(user_id=user_id, article_id=article_id)
        db.session.add(bookmark)

        try:
            db.session.commit()
            return bookmark
        except IntegrityError:
            db.session.rollback()
            return Bookmark.query.filter_by(
                user_id=user_id, article_id=article_id
            ).first()

    def update_notes(self, user_id: int, bookmark_id: int, notes: str | None) -> Bookmark | None:
        bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
        if bookmark is None:
            return None

        bookmark.notes = notes
        db.session.commit()
        return bookmark

    def remove_bookmark(self, user_id: int, bookmark_id: int) -> bool:
        bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
        if bookmark is None:
            return False

        db.session.delete(bookmark)
        db.session.commit()
        return True
