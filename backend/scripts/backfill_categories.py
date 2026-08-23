from app import create_app
from app.models import Article
from app.services.summarization_service import SummarizationService


def backfill_categories() -> None:
    articles = Article.query.filter_by(
        summary_status="completed", category=None
    ).all()

    service = SummarizationService()
    succeeded = 0
    failed = []
    for article in articles:
        try:
            service.summarize(article)
        except Exception as exc:
            print(f"{article.id}: {article.title!r} -> FAILED ({exc})", flush=True)
            failed.append(article.id)
            continue

        succeeded += 1
        print(f"{article.id}: {article.title!r} -> {article.category}", flush=True)

    print(f"Backfilled {succeeded} article(s), {len(failed)} failed: {failed}")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        backfill_categories()
