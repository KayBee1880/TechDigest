from app.extensions import db
from app.models.mixins import TimestampMixin


class Article(TimestampMixin, db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(
        db.Integer, db.ForeignKey("article_sources.id"), nullable=False
    )

    title = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    canonical_url = db.Column(db.String(1000), unique=True, nullable=False)
    title_hash = db.Column(db.String(64), nullable=False, index=True)
    raw_content = db.Column(db.Text)
    category = db.Column(db.String(50))
    published_at = db.Column(db.DateTime, nullable=False)

    summary_status = db.Column(db.String(20), nullable=False, default="pending")

    source = db.relationship("ArticleSource", back_populates="articles")
    summary = db.relationship("Summary", back_populates="article", uselist=False)
    bookmarks = db.relationship("Bookmark", back_populates="article")

    def __repr__(self):
        return f"<Article {self.title!r}>"
