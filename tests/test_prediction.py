from bson.objectid import ObjectId

def test_predict_missing_crop(client, clean_db):
    res = client.post('/api/v1/predict', json={
        "state": "Madhya Pradesh",
        "district": "Indore"
    })
    assert res.status_code == 400

def test_predict_missing_location(client, clean_db):
    res = client.post('/api/v1/predict', json={
        "crop": "Wheat",
        "state": "Madhya Pradesh"
    })
    assert res.status_code == 400

def test_predict_success(client, clean_db):
    res = client.post('/api/v1/predict', json={
        "crop": "Wheat",
        "location": "Indore",
        "state": "Madhya Pradesh",
        "district": "Indore"
    })
    assert res.status_code == 200
    data = res.json
    assert "predicted_prices" in data
    assert "upper_bound" in data
    assert "lower_bound" in data
    assert "trend" in data
    assert "confidence" in data

def test_predict_history_requires_auth(client, clean_db):
    res = client.get('/api/v1/predict/history')
    assert res.status_code == 401

def test_predict_history_saves_when_logged_in(client, auth_headers):
    # Make prediction
    res = client.post('/api/v1/predict', json={
        "crop": "Wheat",
        "location": "Indore",
        "state": "Madhya Pradesh",
        "district": "Indore"
    })
    assert res.status_code == 200
    
    # Check history
    hist_res = client.get('/api/v1/predict/history')
    assert hist_res.status_code == 200
    data = hist_res.json.get("data", [])
    assert len(data) > 0
    assert data[0]["crop"] == "Wheat"

def test_delete_history_entry(client, auth_headers):
    client.post('/api/v1/predict', json={
        "crop": "Wheat",
        "location": "Indore",
        "state": "Madhya Pradesh",
        "district": "Indore"
    })
    hist_res = client.get('/api/v1/predict/history')
    entry_id = hist_res.json["data"][0]["_id"]
    
    del_res = client.delete(f'/api/v1/predict/history/{entry_id}')
    assert del_res.status_code == 200
    
    hist_res2 = client.get('/api/v1/predict/history')
    assert len(hist_res2.json["data"]) == 0

def test_delete_other_users_entry(client, auth_headers, app):
    from utils.db_connection import get_db
    with app.app_context():
        db = get_db()
        res = db.prediction_history.insert_one({
            "user_id": str(ObjectId()),
            "crop": "Rice",
            "state": "Punjab",
            "district": "Amritsar",
            "predicted_price": 2000
        })
        entry_id = str(res.inserted_id)
        
    del_res = client.delete(f'/api/v1/predict/history/{entry_id}')
    assert del_res.status_code == 404
