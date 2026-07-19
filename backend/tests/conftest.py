import pytest

from app import create_app
from app.extensions import db
from app.models import (
    Article,
    ArticleSource,
    Bookmark,
    IngestionJob,
    ProcessingFailure,
    Summary,
    User,
)


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_database(app):
    yield
    db.session.rollback()
    Bookmark.query.delete()
    ProcessingFailure.query.delete()
    Summary.query.delete()
    IngestionJob.query.delete()
    Article.query.delete()
    User.query.delete()
    ArticleSource.query.delete()
    db.session.commit()
