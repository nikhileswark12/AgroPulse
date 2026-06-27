import pytest
from app import create_app
from utils.db_connection import get_db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def clean_db(app):
    db = get_db()
    db.users.delete_many({})
    db.prediction_history.delete_many({})
    yield
    db.users.delete_many({})
    db.prediction_history.delete_many({})

@pytest.fixture
def auth_headers(client, clean_db, app):
    db = get_db()
    
    # Register a user
    client.post('/api/v1/auth/register', json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "Password123!"
    })
    
    # Verify directly in DB
    db.users.update_one(
        {"email": "test@example.com"},
        {"$set": {"verified": True}}
    )
    
    # Log in to set the session cookie in the test client
    response = client.post('/api/v1/auth/login', json={
        "email": "test@example.com",
        "password": "Password123!"
    })
    
    cookie = response.headers.get('Set-Cookie', '')
    
    return {'Cookie': cookie} if cookie else {}
