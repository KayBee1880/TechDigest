from app.extensions import db
from app.models import Article


class ArticleService:
    DEFAULT_PER_PAGE = 20
    MAX_PER_PAGE = 100

    def list_articles(
        self,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
        source_id: int | None = None,
        category: str | None = None,
        q: str | None = None,
    ):
        per_page = min(per_page, self.MAX_PER_PAGE)
        query = Article.query.filter_by(summary_status="completed").order_by(
            Article.published_at.desc()
        )

        if source_id is not None:
            query = query.filter_by(source_id=source_id)

        if category:
            query = query.filter_by(category=category)

        if q:
            query = query.filter(Article.title.ilike(f"%{q}%"))

        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_article(self, article_id: int) -> Article | None:
        return db.session.get(Article, article_id)
