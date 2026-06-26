import requests

BASE_URL = "http://localhost:5000/api"

def test_prediction_history():
    sess = requests.Session()
    
    # 1. Login
    print("Logging in...")
    res = sess.post(f"{BASE_URL}/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    print(res.status_code)

    # 2. Predict with specific fields
    print("\nMaking prediction...")
    res = sess.post(f"{BASE_URL}/predict", json={
        "crop": "Corn",
        "state": "Maharashtra",
        "location": "Pune",
        "district": "Pune District",
        "quantity": 250
    })
    print(res.status_code)
    
    # 3. Check history for the exact fields
    print("\nChecking history fields...")
    res = sess.get(f"{BASE_URL}/predict/history")
    print(res.status_code)
    history_data = res.json()
    if history_data.get('history'):
        entry = history_data['history'][0]
        print("Fields in latest entry:")
        expected_fields = ["user_id", "crop", "state", "district", "quantity", 
                           "predicted_prices", "upper_bound", "lower_bound", 
                           "recommendation", "expected_gain", "best_market", 
                           "confidence", "trend", "created_at"]
        for f in expected_fields:
            val = entry.get(f)
            try:
                print(f"  {f}: {val}")
            except UnicodeEncodeError:
                print(f"  {f}: {str(val).encode('ascii', 'ignore').decode()}")
            
    # 4. Logout
    print("\nLogging out...")
    res = sess.post(f"{BASE_URL}/auth/logout")
    print(res.status_code)
    
    # 5. Check history unauthorized
    print("\nChecking history (unauthorized)...")
    res = sess.get(f"{BASE_URL}/predict/history")
    print(res.status_code)
    print(res.json())

if __name__ == "__main__":
    test_prediction_history()
