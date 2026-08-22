from celery import shared_task

from app.extensions import db
from app.models import Article, ArticleSource, ProcessingFailure
from app.services.news_ingestion_service import NewsIngestionService
from app.services.summarization_service import SummarizationService


@shared_task
def ingest_all_sources_task() -> None:
    source_ids = [
        source_id
        for (source_id,) in db.session.query(ArticleSource.id)
        .filter_by(is_active=True)
        .all()
    ]
    for source_id in source_ids:
        ingest_source_task.delay(source_id)


@shared_task
def ingest_source_task(source_id: int) -> None:
    source = db.session.get(ArticleSource, source_id)
    if source is None:
        return

    NewsIngestionService().ingest(
        source,
        on_created=lambda article: summarize_article_task.delay(article.id),
    )


@shared_task(bind=True, max_retries=5)
def summarize_article_task(self, article_id: int) -> None:
    article = db.session.get(Article, article_id)
    if article is None or article.summary_status == "completed":
        return

    if not article.raw_content:
        article.summary_status = "unavailable"
        db.session.commit()
        return

    try:
        summary = SummarizationService().summarize(article)
        summary.retry_count = self.request.retries
        db.session.commit()
    except Exception as exc:
        db.session.add(
            ProcessingFailure(
                article_id=article_id,
                attempt_number=self.request.retries + 1,
                error_message=str(exc),
            )
        )
        db.session.commit()

        if self.request.retries >= self.max_retries:
            article.summary_status = "failed"
            db.session.commit()
            return

        raise self.retry(exc=exc, countdown=2**self.request.retries * 10)
