from app import create_app
from app.models import ArticleSource
from app.services.news_ingestion_service import NewsIngestionService


def ingest_all_sources() -> None:
    service = NewsIngestionService()
    sources = ArticleSource.query.filter_by(is_active=True).all()

    for source in sources:
        job = service.ingest(source)
        print(
            f"{source.name}: {job.status} "
            f"({job.articles_created} new / {job.articles_found} found)"
        )


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        ingest_all_sources()
