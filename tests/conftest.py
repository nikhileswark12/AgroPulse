import pytest
from app import create_app
from utils.db_connection import get_db


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def _test_database(app):
    db = get_db()
    configured_name = str(app.config.get("DATABASE_NAME", ""))
    actual_name = str(db.name)
    if "test" not in configured_name.casefold() or actual_name != configured_name:
        raise RuntimeError("Refusing to clean a database that is not the configured test database")
    return db


@pytest.fixture
def clean_db(app):
    with app.app_context():
        database = _test_database(app)
        database.users.delete_many({})
        database.prediction_history.delete_many({})
    yield
    with app.app_context():
        database = _test_database(app)
        database.users.delete_many({})
        database.prediction_history.delete_many({})


@pytest.fixture
def auth_headers(client, clean_db, app):
    client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "Password123!"
    })
    with app.app_context():
        db = _test_database(app)
        db.users.update_one(
            {"email_normalized": "test@example.com"},
            {"$set": {"verified": True}}
        )
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "Password123!"
    })
    cookie = response.headers.get("Set-Cookie", "")
    return {"Cookie": cookie} if cookie else {}
