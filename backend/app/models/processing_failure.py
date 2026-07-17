from datetime import datetime

from app.extensions import db


class ProcessingFailure(db.Model):
    __tablename__ = "processing_failures"

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)

    attempt_number = db.Column(db.Integer, nullable=False)
    error_message = db.Column(db.Text, nullable=False)
    occurred_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    article = db.relationship("Article")

    def __repr__(self):
        return (
            f"<ProcessingFailure article_id={self.article_id} "
            f"attempt={self.attempt_number}>"
        )
