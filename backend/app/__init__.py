import os

from flask import Flask
from flask_cors import CORS

from app.celery_app import celery_init_app
from app.config import config
from app.extensions import db, migrate


def create_app(config_name=None):
    config_name = config_name or os.environ.get("APP_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    CORS(app, origins=app.config["CORS_ORIGINS"])
    db.init_app(app)
    migrate.init_app(app, db)
    celery_init_app(app)

    from app import models, tasks  # noqa: F401
    from app.api.articles import articles_bp
    from app.api.auth import auth_bp
    from app.api.bookmarks import bookmarks_bp
    from app.api.health import health_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(bookmarks_bp)

    return app
