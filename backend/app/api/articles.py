from flask import Blueprint, jsonify, request

from app.constants import ARTICLE_CATEGORIES
from app.schemas.article_schema import ArticleSchema
from app.services.article_service import ArticleService

articles_bp = Blueprint("articles", __name__)

article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)


@articles_bp.route("/api/articles/categories")
def list_categories():
    return jsonify(ARTICLE_CATEGORIES)


@articles_bp.route("/api/articles")
def list_articles():
    service = ArticleService()

    page = request.args.get("page", 1, type=int) or 1
    per_page = request.args.get("per_page", ArticleService.DEFAULT_PER_PAGE, type=int) or (
        ArticleService.DEFAULT_PER_PAGE
    )
    source_id = request.args.get("source_id", type=int)
    category = request.args.get("category")
    q = request.args.get("q")

    pagination = service.list_articles(
        page=page, per_page=per_page, source_id=source_id, category=category, q=q
    )

    return jsonify(
        {
            "items": articles_schema.dump(pagination.items),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }
    )


@articles_bp.route("/api/articles/<int:article_id>")
def get_article(article_id):
    service = ArticleService()
    article = service.get_article(article_id)

    if article is None:
        return jsonify(error="Article not found"), 404

    return jsonify(article_schema.dump(article))
