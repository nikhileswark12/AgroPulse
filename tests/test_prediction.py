import pytest
from bson.objectid import ObjectId


@pytest.fixture(autouse=True)
def mock_prediction_model(monkeypatch):
    import routes.prediction_routes as prediction_routes

    def predict_price(crop, location, state="Madhya Pradesh", quantity=100):
        return {
            "success": True,
            "predicted_price": 2000.0,
            "predicted_prices": [2000.0, 2001.0, 2002.0, 2003.0, 2004.0, 2005.0, 2006.0],
            "upper_bound": [2080.0, 2081.0, 2082.0, 2083.0, 2084.0, 2085.0, 2086.0],
            "lower_bound": [1920.0, 1921.0, 1922.0, 1923.0, 1924.0, 1925.0, 1926.0],
            "recommendation": "SELL NOW",
            "expected_gain": "₹6 / quintal",
            "best_market": f"{location} APMC",
            "trend": "stable",
            "confidence": "low",
            "model_type": "test_fixture"
        }

    monkeypatch.setattr(prediction_routes, "ML_AVAILABLE", True)
    monkeypatch.setattr(prediction_routes.ml_predict, "predict_price", predict_price)

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



def test_predict_returns_service_unavailable_when_model_missing(client, monkeypatch):
    import routes.prediction_routes as prediction_routes

    monkeypatch.setattr(prediction_routes, "ML_AVAILABLE", False)
    response = client.post("/api/v1/predict", json={
        "crop": "Wheat",
        "location": "Indore",
        "state": "Madhya Pradesh"
    })

    assert response.status_code == 503
    assert response.json["error"] == "model_unavailable"
    assert "predicted_prices" not in response.json


def test_predict_rejects_non_object_json(client):
    response = client.post("/api/v1/predict", data='["Wheat"]', content_type="application/json")

    assert response.status_code == 400
    assert response.json["error"] == "invalid_request"
