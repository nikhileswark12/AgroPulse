def test_health_returns_ok(client):
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json.get("status") == "ok"

def test_health_shows_model_status(client):
    res = client.get('/health')
    assert "model_loaded" in res.json
    assert isinstance(res.json["model_loaded"], bool)

def test_health_shows_db_status(client):
    res = client.get('/health')
    assert "db_connected" in res.json
    assert isinstance(res.json["db_connected"], bool)
