from app.extensions import db
from app.models.mixins import TimestampMixin


class Summary(TimestampMixin, db.Model):
    __tablename__ = "summaries"

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(
        db.Integer, db.ForeignKey("articles.id"), unique=True, nullable=False
    )

    content = db.Column(db.Text)
    provider = db.Column(db.String(50), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    retry_count = db.Column(db.Integer, nullable=False, default=0)

    article = db.relationship("Article", back_populates="summary")

    def __repr__(self):
        return f"<Summary article_id={self.article_id}>"
