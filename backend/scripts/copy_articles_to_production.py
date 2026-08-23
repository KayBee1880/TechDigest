import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

ARTICLE_COLUMNS = [
    "id",
    "source_id",
    "title",
    "url",
    "canonical_url",
    "title_hash",
    "raw_content",
    "category",
    "published_at",
    "summary_status",
    "created_at",
    "updated_at",
]
SUMMARY_COLUMNS = [
    "id",
    "article_id",
    "content",
    "provider",
    "model_name",
    "retry_count",
    "created_at",
    "updated_at",
]


def copy_completed_articles(local_url: str, target_url: str) -> None:
    local_engine = create_engine(local_url)
    target_engine = create_engine(target_url)

    with local_engine.connect() as conn:
        articles = conn.execute(
            text(
                f"SELECT {', '.join(ARTICLE_COLUMNS)} FROM articles "
                "WHERE summary_status = 'completed'"
            )
        ).mappings().all()
        article_ids = [a["id"] for a in articles]
        summaries = conn.execute(
            text(
                f"SELECT {', '.join(SUMMARY_COLUMNS)} FROM summaries "
                "WHERE article_id = ANY(:ids)"
            ),
            {"ids": article_ids},
        ).mappings().all()

    with target_engine.begin() as conn:
        for row in articles:
            conn.execute(
                text(
                    f"INSERT INTO articles ({', '.join(ARTICLE_COLUMNS)}) "
                    f"VALUES ({', '.join(f':{c}' for c in ARTICLE_COLUMNS)}) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                dict(row),
            )
        for row in summaries:
            conn.execute(
                text(
                    f"INSERT INTO summaries ({', '.join(SUMMARY_COLUMNS)}) "
                    f"VALUES ({', '.join(f':{c}' for c in SUMMARY_COLUMNS)}) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                dict(row),
            )
        conn.execute(text("SELECT setval('articles_id_seq', (SELECT MAX(id) FROM articles))"))
        conn.execute(text("SELECT setval('summaries_id_seq', (SELECT MAX(id) FROM summaries))"))

    print(f"Copied {len(articles)} article(s) and {len(summaries)} summary(ies).")


if __name__ == "__main__":
    copy_completed_articles(
        local_url=os.environ["DATABASE_URL"],
        target_url=os.environ["NEON_DATABASE_URL"],
    )
