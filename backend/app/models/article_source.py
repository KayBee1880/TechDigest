from app.extensions import db
from app.models.mixins import TimestampMixin


class ArticleSource(TimestampMixin, db.Model):
    __tablename__ = "article_sources"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    source_type = db.Column(db.String(20), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    articles = db.relationship("Article", back_populates="source")

    def __repr__(self):
        return f"<ArticleSource {self.name}>"
