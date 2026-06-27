def test_register_success(client, clean_db):
    res = client.post('/api/v1/auth/register', json={
        "name": "New User",
        "email": "new@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 201

def test_register_duplicate_email(client, clean_db):
    client.post('/api/v1/auth/register', json={
        "name": "New User",
        "email": "new@example.com",
        "password": "Password123!"
    })
    res = client.post('/api/v1/auth/register', json={
        "name": "New User2",
        "email": "new@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 409

def test_register_short_password(client, clean_db):
    res = client.post('/api/v1/auth/register', json={
        "name": "New User",
        "email": "new@example.com",
        "password": "short"
    })
    assert res.status_code == 400

def test_login_unverified(client, clean_db):
    client.post('/api/v1/auth/register', json={
        "name": "New User",
        "email": "new@example.com",
        "password": "Password123!"
    })
    res = client.post('/api/v1/auth/login', json={
        "email": "new@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 401

def test_login_success(client, clean_db, app):
    client.post('/api/v1/auth/register', json={
        "name": "New User",
        "email": "new@example.com",
        "password": "Password123!"
    })
    from utils.db_connection import get_db
    with app.app_context():
        db = get_db()
        db.users.update_one({"email": "new@example.com"}, {"$set": {"verified": True}})
        
    res = client.post('/api/v1/auth/login', json={
        "email": "new@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 200
    assert "user" in res.json or "email" in str(res.json)

def test_login_wrong_password(client, clean_db, app):
    client.post('/api/v1/auth/register', json={
        "name": "New User",
        "email": "new@example.com",
        "password": "Password123!"
    })
    from utils.db_connection import get_db
    with app.app_context():
        db = get_db()
        db.users.update_one({"email": "new@example.com"}, {"$set": {"verified": True}})
        
    res = client.post('/api/v1/auth/login', json={
        "email": "new@example.com",
        "password": "WrongPassword123!"
    })
    assert res.status_code == 401

def test_logout(client, auth_headers):
    # test_logout: POST /api/v1/auth/logout clears session, subsequent /api/v1/auth/check returns authenticated false
    res = client.post('/api/v1/auth/logout')
    
    check_res = client.get('/api/v1/auth/check')
    assert check_res.json.get("authenticated") == False
