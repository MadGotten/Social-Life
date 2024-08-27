import pytest
from flask_login import FlaskLoginClient
from werkzeug.security import generate_password_hash
from website import create_app, db
from website.models import User


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authorized_client(app):
    app.test_client_class = FlaskLoginClient
    user = User.query.get(1)
    with app.test_client(user=user) as client:
        return client


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()

        user = User(
            email="user1@test.com",
            username="user1",
            password=generate_password_hash("TestPassword123!"),
            first_name="User",
            last_name="One",
        )
        db.session.add(user)

        db.session.commit()

    yield db
