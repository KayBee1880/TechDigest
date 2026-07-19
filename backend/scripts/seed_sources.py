from app import create_app
from app.extensions import db
from app.models import ArticleSource

SOURCES = [
    {
        "name": "Hacker News",
        "source_type": "api",
        "url": "https://hacker-news.firebaseio.com/v0/topstories.json",
    },
    {
        "name": "TechCrunch",
        "source_type": "rss",
        "url": "https://techcrunch.com/feed/",
    },
    {
        "name": "Ars Technica",
        "source_type": "rss",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
    },
    {
        "name": "The Verge",
        "source_type": "rss",
        "url": "https://www.theverge.com/rss/index.xml",
    },
]


def seed_sources() -> None:
    for source_data in SOURCES:
        exists = ArticleSource.query.filter_by(name=source_data["name"]).first()
        if exists is not None:
            continue
        db.session.add(ArticleSource(**source_data))

    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_sources()
