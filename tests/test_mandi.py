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

def test_compare_with_coordinates(client):
    # Test with coordinates for Indore (22.7196, 75.8577)
    res = client.get('/api/v1/mandi/compare?crop=Wheat&lat=22.7196&lon=75.8577')
    assert res.status_code == 200
    assert "markets" in res.json
    for market in res.json["markets"]:
        # Distance should either be "X.X km" or "—" depending on coords match
        assert "distance" in market
        dist = market["distance"]
        assert dist == "—" or " km" in dist
