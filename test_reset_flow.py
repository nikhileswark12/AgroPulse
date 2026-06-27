import requests
import re
import time
from utils.db_connection import get_db

BASE_URL = "http://localhost:5000/api"
EMAIL = "test@example.com"

def run_test():
    # Setup test user using pymongo
    db = get_db()
    user = db.users.find_one({"email": EMAIL})
    if not user:
        print("User not found, registering...")
        requests.post(f"{BASE_URL}/auth/register", json={
            "name": "Test", "email": EMAIL, "password": "password123"
        })
    db.users.update_one({"email": EMAIL}, {"$set": {"verified": True}})

    print("Requesting password reset...")
    res = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": EMAIL})
    print(res.status_code, res.json())

    # Wait for the server log to flush
    time.sleep(1)

    print("\nReading token from logs/agropulse.log...")
    with open('logs/agropulse.log', 'r') as f:
        log_content = f.read()

    # Look for the fallback link in the log
    matches = re.findall(r'/password-reset/([a-zA-Z0-9_\-\.]+)', log_content)
    if not matches:
        print("No reset token found in logs/agropulse.log")
        return
        
    token = matches[-1]
    print(f"Found token: {token}")

    print("\nSetting new password...")
    res = requests.post(f"{BASE_URL}/auth/reset-password", json={
        "token": token,
        "new_password": "newpassword123",
        "confirm_password": "newpassword123"
    })
    print(res.status_code, res.json())

    print("\nAttempting login with OLD password (should fail)...")
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": "password123"})
    print(res.status_code, res.json())

    print("\nAttempting login with NEW password (should succeed)...")
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": "newpassword123"})
    print(res.status_code, res.json())

    print("\nAttempting to reuse old reset token (should fail)...")
    res = requests.post(f"{BASE_URL}/auth/reset-password", json={
        "token": token,
        "new_password": "anothrepassword",
        "confirm_password": "anothrepassword"
    })
    print(res.status_code, res.json())
    
    # Revert password for future tests
    db.users.update_one({"email": EMAIL}, {"$set": {"password": "$2b$12$somehashthatworksforpassword123"}})

if __name__ == '__main__':
    run_test()
