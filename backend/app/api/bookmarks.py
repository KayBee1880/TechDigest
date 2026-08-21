from flask import Blueprint, g, jsonify, request
from marshmallow import ValidationError

from app.api.auth import login_required
from app.schemas.bookmark_schema import BookmarkCreateSchema, BookmarkSchema
from app.services.bookmark_service import BookmarkService

bookmarks_bp = Blueprint("bookmarks", __name__)

bookmark_schema = BookmarkSchema()
bookmarks_schema = BookmarkSchema(many=True)
bookmark_create_schema = BookmarkCreateSchema()


@bookmarks_bp.route("/api/bookmarks")
@login_required
def list_bookmarks():
    service = BookmarkService()

    page = request.args.get("page", 1, type=int) or 1
    per_page = request.args.get(
        "per_page", BookmarkService.DEFAULT_PER_PAGE, type=int
    ) or BookmarkService.DEFAULT_PER_PAGE

    pagination = service.list_bookmarks(
        user_id=g.current_user_id, page=page, per_page=per_page
    )

    return jsonify(
        {
            "items": bookmarks_schema.dump(pagination.items),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }
    )


@bookmarks_bp.route("/api/bookmarks", methods=["POST"])
@login_required
def create_bookmark():
    try:
        data = bookmark_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify(errors=err.messages), 400

    service = BookmarkService()
    bookmark = service.add_bookmark(
        user_id=g.current_user_id, article_id=data["article_id"]
    )

    if bookmark is None:
        return jsonify(error="Article not found"), 404

    return jsonify(bookmark_schema.dump(bookmark)), 201


@bookmarks_bp.route("/api/bookmarks/<int:bookmark_id>", methods=["DELETE"])
@login_required
def delete_bookmark(bookmark_id):
    service = BookmarkService()
    removed = service.remove_bookmark(
        user_id=g.current_user_id, bookmark_id=bookmark_id
    )

    if not removed:
        return jsonify(error="Bookmark not found"), 404

    return "", 204
