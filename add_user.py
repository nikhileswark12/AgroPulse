from werkzeug.security import generate_password_hash
from utils.db_connection import get_db

# Connect to MongoDB
db = get_db()
users_collection = db['users']

# Create test user
test_user = {
    'name': 'Test User',
    'email': 'test@agropulse.com',
    'password': generate_password_hash('test123')
}

# Check if exists
existing = users_collection.find_one({'email': 'test@agropulse.com'})

if existing:
    print("User already exists!")
    print("Email: test@agropulse.com")
    print("Password: test123")
else:
    result = users_collection.insert_one(test_user)
    print(f"✅ User created! ID: {result.inserted_id}")
    print("Email: test@agropulse.com")
    print("Password: test123")

# List all users
print("\n📋 All users:")
for user in users_collection.find():
    print(f"  - {user['name']} ({user['email']})")