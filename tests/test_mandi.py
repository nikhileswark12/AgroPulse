def test_compare_missing_crop(client):
    res = client.get('/api/v1/mandi/compare')
    assert res.status_code == 400

def test_compare_valid_crop(client):
    res = client.get('/api/v1/mandi/compare?crop=Wheat')
    assert res.status_code == 200
    assert "markets" in res.json
    assert isinstance(res.json["markets"], list)

def test_compare_unknown_crop(client):
    res = client.get('/api/v1/mandi/compare?crop=UnknownCrop')
    assert res.status_code == 200
    assert "markets" in res.json
    assert len(res.json["markets"]) == 0
