import requests

BASE_URL = "http://localhost:5000/api"

def test_prediction_flow():
    sess = requests.Session()
    
    # 1. Login
    print("Logging in...")
    res = sess.post(f"{BASE_URL}/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    print(res.status_code, res.json())
    
    if res.status_code != 200:
        print("Login failed, aborting test.")
        return

    # 2. Make Prediction
    print("\nMaking prediction...")
    res = sess.post(f"{BASE_URL}/predict", json={
        "crop": "Wheat",
        "state": "Madhya Pradesh",
        "location": "Bhopal",
        "quantity": 100
    })
    print(res.status_code)
    prediction_data = res.json()
    if 'predicted_prices' in prediction_data:
        print("Prediction successful, contains predicted_prices")
    else:
        print("Prediction failed or missing predicted_prices:", prediction_data)

    # 3. Check History
    print("\nFetching history...")
    res = sess.get(f"{BASE_URL}/predict/history")
    print(res.status_code)
    history_data = res.json()
    
    if history_data.get('success') and len(history_data.get('history', [])) > 0:
        print(f"History saved! Found {len(history_data['history'])} records.")
    else:
        print("History empty or failed:", history_data)
        
    # 4. Check Metadata vs Model-Info
    print("\nChecking metadata endpoints...")
    res1 = requests.get(f"{BASE_URL}/predict/model-info")
    res2 = requests.get(f"{BASE_URL}/predict/metadata")
    
    print(f"model-info status: {res1.status_code}")
    print(f"metadata status: {res2.status_code}")
    
    if res1.json() == res2.json():
        print("Success! /predict/model-info and /predict/metadata return identical JSON.")
    else:
        print("Mismatch between metadata endpoints!")

if __name__ == "__main__":
    test_prediction_flow()
