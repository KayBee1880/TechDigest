from datetime import timedelta

import jwt
from flask import current_app
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User
from app.utils.time import utc_now


class UserService:
    TOKEN_EXPIRY = timedelta(days=7)

    def register(self, email: str, password: str) -> User | None:
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)

        try:
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return None

    def authenticate(self, email: str, password: str) -> User | None:
        user = User.query.filter_by(email=email).first()

        if user is None or not check_password_hash(user.password_hash, password):
            return None

        return user

    def generate_token(self, user: User) -> str:
        payload = {"sub": str(user.id), "exp": utc_now() + self.TOKEN_EXPIRY}
        return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")

    @staticmethod
    def decode_token(token: str) -> int | None:
        try:
            payload = jwt.decode(
                token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
            )
            return int(payload["sub"])
        except (jwt.PyJWTError, ValueError, KeyError):
            return None
