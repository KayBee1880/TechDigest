from app.extensions import db
from app.models.mixins import TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    bookmarks = db.relationship("Bookmark", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"
