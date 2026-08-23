from marshmallow import Schema, fields

from app.schemas.article_schema import ArticleSchema


class BookmarkSchema(Schema):
    id = fields.Int()
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    article = fields.Nested(ArticleSchema)


class BookmarkCreateSchema(Schema):
    article_id = fields.Int(required=True)


class BookmarkUpdateSchema(Schema):
    notes = fields.Str(required=True, allow_none=True)
