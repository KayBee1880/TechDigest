from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Int()
    email = fields.Email()
    created_at = fields.DateTime()


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
