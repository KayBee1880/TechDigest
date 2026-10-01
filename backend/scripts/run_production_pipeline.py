import sys

from sqlalchemy import func

from app import create_app
from app.extensions import db
from app.models import Article, ArticleSource, ProcessingFailure
from app.services.news_ingestion_service import NewsIngestionService
from app.services.summarization_service import SummarizationService

MAX_ATTEMPTS = 5
MAX_SUMMARIES_PER_RUN = 25


def summarize_one(article: Article) -> bool | None:
    """True if summarized, False if the attempt failed, None if nothing was attempted."""
    if article.summary_status == "completed":
        return None

    if not article.raw_content:
        article.summary_status = "unavailable"
        db.session.commit()
        return None

    attempt_number = ProcessingFailure.query.filter_by(article_id=article.id).count() + 1

    try:
        SummarizationService().summarize(article)
        print(f"{article.id}: {article.title!r} -> {article.category}")
        return True
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
        return False


def select_pending(limit: int) -> list[Article]:
    """Pending articles to attempt this run: articles that have already failed at least
    once come first (so a brief rate-limit spike can't strand them behind an endless
    stream of newer arrivals), newest first within each group."""
    failure_counts = (
        db.session.query(
            ProcessingFailure.article_id.label("article_id"),
            func.count(ProcessingFailure.id).label("failures"),
        )
        .group_by(ProcessingFailure.article_id)
        .subquery()
    )
    return (
        Article.query.outerjoin(failure_counts, Article.id == failure_counts.c.article_id)
        .filter(Article.summary_status == "pending")
        .order_by(
            func.coalesce(failure_counts.c.failures, 0).desc(),
            Article.published_at.desc(),
        )
        .limit(limit)
        .all()
    )


def run_pipeline() -> tuple[int, int]:
    """Ingest, then summarize pending articles. Returns (attempted, succeeded)."""
    ingestion_service = NewsIngestionService()
    sources = ArticleSource.query.filter_by(is_active=True).all()

    for source in sources:
        job = ingestion_service.ingest(source)
        print(
            f"{source.name}: {job.status} "
            f"({job.articles_created} new / {job.articles_found} found)"
        )

    # Articles with no body text can never be summarized; resolve them in bulk first so
    # they don't use up the per-run budget meant for articles that actually can be.
    Article.query.filter(
        Article.summary_status == "pending",
        db.or_(Article.raw_content.is_(None), Article.raw_content == ""),
    ).update({"summary_status": "unavailable"}, synchronize_session=False)
    db.session.commit()

    pending = select_pending(MAX_SUMMARIES_PER_RUN)
    print(f"Summarizing {len(pending)} pending article(s) (retries first, then newest)...")

    results = [summarize_one(article) for article in pending]
    attempted = sum(1 for r in results if r is not None)
    succeeded = sum(1 for r in results if r)
    print(f"Summarized {succeeded} of {attempted} attempted.")
    return attempted, succeeded


def exit_code(attempted: int, succeeded: int) -> int:
    # Per-article failures are handled and retried on later runs, so they don't fail the
    # job on their own. But a run that attempted work and got *none* of it through means
    # something systemic is wrong (a retired model, a bad key, an outage) - and that must
    # show up as a red run instead of a green one, or it can go unnoticed for weeks.
    return 1 if attempted and not succeeded else 0


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        attempted, succeeded = run_pipeline()
    code = exit_code(attempted, succeeded)
    if code:
        print(f"All {attempted} summarization attempt(s) this run failed - failing the job.")
    sys.exit(code)
