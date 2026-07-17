from datetime import datetime

from app.extensions import db


class IngestionJob(db.Model):
    __tablename__ = "ingestion_jobs"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(
        db.Integer, db.ForeignKey("article_sources.id"), nullable=False
    )

    status = db.Column(db.String(20), nullable=False, default="running")
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    articles_found = db.Column(db.Integer, nullable=False, default=0)
    articles_created = db.Column(db.Integer, nullable=False, default=0)
    error_message = db.Column(db.Text)

    source = db.relationship("ArticleSource")

    def __repr__(self):
        return f"<IngestionJob source_id={self.source_id} status={self.status}>"
