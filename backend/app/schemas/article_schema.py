from marshmallow import Schema, fields


class ArticleSourceSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class SummarySchema(Schema):
    content = fields.Str()
    provider = fields.Str()


class ArticleSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    url = fields.Str()
    category = fields.Str()
    published_at = fields.DateTime()
    summary_status = fields.Str()
    source = fields.Nested(ArticleSourceSchema)
    summary = fields.Nested(SummarySchema, allow_none=True)
