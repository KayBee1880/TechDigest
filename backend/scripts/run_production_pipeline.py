from app import create_app
from app.extensions import db
from app.models import Article, ArticleSource, ProcessingFailure
from app.services.news_ingestion_service import NewsIngestionService
from app.services.summarization_service import SummarizationService

MAX_ATTEMPTS = 5


def summarize_one(article: Article) -> None:
    if article.summary_status == "completed":
        return

    if not article.raw_content:
        article.summary_status = "unavailable"
        db.session.commit()
        return

    attempt_number = ProcessingFailure.query.filter_by(article_id=article.id).count() + 1

    try:
        SummarizationService().summarize(article)
        print(f"{article.id}: {article.title!r} -> {article.category}")
    except Exception as exc:
        db.session.add(
            ProcessingFailure(
                article_id=article.id, attempt_number=attempt_number, error_message=str(exc)
            )
        )
        if attempt_number >= MAX_ATTEMPTS:
            article.summary_status = "failed"
        db.session.commit()
        print(f"{article.id}: {article.title!r} -> FAILED attempt {attempt_number} ({exc})")


def run_pipeline() -> None:
    ingestion_service = NewsIngestionService()
    sources = ArticleSource.query.filter_by(is_active=True).all()

    for source in sources:
        job = ingestion_service.ingest(source)
        print(
            f"{source.name}: {job.status} "
            f"({job.articles_created} new / {job.articles_found} found)"
        )

    pending = Article.query.filter_by(summary_status="pending").all()
    print(f"Summarizing {len(pending)} pending article(s)...")
    for article in pending:
        summarize_one(article)


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run_pipeline()
