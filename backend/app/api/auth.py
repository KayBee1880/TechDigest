from functools import wraps

from flask import Blueprint, g, jsonify, request
from marshmallow import ValidationError

from app.schemas.user_schema import LoginSchema, RegisterSchema, UserSchema
from app.services.user_service import UserService

auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify(error="Missing or malformed Authorization header"), 401

        token = auth_header.removeprefix("Bearer ")
        user_id = UserService.decode_token(token)
        if user_id is None:
            return jsonify(error="Invalid or expired token"), 401

        g.current_user_id = user_id
        return view(*args, **kwargs)

    return wrapped_view

user_schema = UserSchema()
register_schema = RegisterSchema()
login_schema = LoginSchema()


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = register_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify(errors=err.messages), 400

    service = UserService()
    user = service.register(email=data["email"], password=data["password"])

    if user is None:
        return jsonify(error="Email already registered"), 409

    token = service.generate_token(user)
    return jsonify(user=user_schema.dump(user), token=token), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = login_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify(errors=err.messages), 400

    service = UserService()
    user = service.authenticate(email=data["email"], password=data["password"])

    if user is None:
        return jsonify(error="Invalid email or password"), 401

    token = service.generate_token(user)
    return jsonify(user=user_schema.dump(user), token=token)
