from datetime import datetime

from app.extensions import db


class Bookmark(db.Model):
    __tablename__ = "bookmarks"
    __table_args__ = (db.UniqueConstraint("user_id", "article_id"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="bookmarks")
    article = db.relationship("Article", back_populates="bookmarks")

    def __repr__(self):
        return f"<Bookmark user_id={self.user_id} article_id={self.article_id}>"
