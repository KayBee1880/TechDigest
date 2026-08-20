import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY = {
        "broker_url": os.environ.get("REDIS_URL"),
        "result_backend": os.environ.get("REDIS_URL"),
        "task_ignore_result": True,
        "beat_schedule": {
            "ingest-all-sources": {
                "task": "app.tasks.ingest_all_sources_task",
                "schedule": timedelta(minutes=15),
            },
        },
    }


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", os.environ.get("DATABASE_URL")
    )
    CELERY = {
        **Config.CELERY,
        "task_always_eager": True,
    }


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
