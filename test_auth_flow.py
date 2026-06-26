import requests
import re
import time

BASE_URL = "http://localhost:5000/api/auth"

def test_auth_flow():
    # 1. Register
    print("Testing Registration...")
    res = requests.post(f"{BASE_URL}/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    })
    print(res.status_code, res.json())
    
    time.sleep(1) # wait for log to flush

    # 2. Login unverified
    print("\nTesting Unverified Login...")
    res = requests.post(f"{BASE_URL}/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    print(res.status_code, res.json())

    # 3. Read log file to get verification link
    log_path = "server.log"
    verify_url = None
    import os
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            content = f.read()
            # Match the last occurrence
            matches = re.findall(r'(http://localhost:5000/api/auth/verify/[^\s]+)', content)
            if matches:
                verify_url = matches[-1]
                
    if not verify_url:
        print("Could not find verification link in logs. Make sure mail is configured or fallback logs work.")
        return

    print("\nFound verify URL:", verify_url)

    # 4. Visit verification link
    print("Testing Verification...")
    res = requests.get(verify_url, allow_redirects=False)
    print(res.status_code, res.headers.get('Location'))

    # 5. Login verified
    print("\nTesting Verified Login...")
    sess = requests.Session()
    res = sess.post(f"{BASE_URL}/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    print(res.status_code, res.json())
    
    # Check session cookie
    print("Cookies:", sess.cookies.get_dict())
    
    # 6. Incorrect password
    print("\nTesting Incorrect Password...")
    res = requests.post(f"{BASE_URL}/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    print(res.status_code, res.json())

if __name__ == "__main__":
    test_auth_flow()
