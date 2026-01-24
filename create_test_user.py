"""
Script to create a test user in the database
Run this once to create a test user for login
"""

from werkzeug.security import generate_password_hash
from utils.db_connection import db
from pymongo.errors import ConnectionFailure

def create_test_user():
    """Create a test user in the database"""
    
    try:
        # Connect to database
        print("Connecting to database...")
        db.connect()
        
        # Test the connection
        db.client.admin.command('ping')
        print("✅ Database connected successfully!")
        
        # Test user credentials
        test_user = {
            'name': 'Test User',
            'email': 'test@agropulse.com',
            'password': generate_password_hash('test123')  # Password: test123
        }
        
        # Check if user already exists
        print(f"\nChecking if user exists: {test_user['email']}")
        existing_user = db.get_collection('users').find_one({'email': test_user['email']})
        
        if existing_user:
            print(f"\n❌ User already exists: {test_user['email']}")
            print("=" * 60)
            print("You can login with:")
            print(f"   Email: {test_user['email']}")
            print("   Password: test123")
            print("=" * 60)
        else:
            # Insert the test user
            print(f"\nCreating user: {test_user['email']}")
            result = db.get_collection('users').insert_one(test_user)
            
            if result.inserted_id:
                print("\n" + "=" * 60)
                print("✅ Test user created successfully!")
                print("=" * 60)
                print(f"Name: {test_user['name']}")
                print(f"Email: {test_user['email']}")
                print("Password: test123")
                print("=" * 60)
                print("\n🌐 You can now login at: http://localhost:5000/login")
                print("=" * 60)
            else:
                print("\n❌ Failed to create test user")
        
        # List all users in the database
        print("\n📋 All users in database:")
        users = db.get_collection('users').find()
        user_count = 0
        for user in users:
            user_count += 1
            print(f"   {user_count}. {user['name']} ({user['email']})")
        
        if user_count == 0:
            print("   (No users found)")
        
    except ConnectionFailure as e:
        print(f"\n❌ Database connection failed: {e}")
        print("Make sure MongoDB is running!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Close connection
        print("\nClosing database connection...")
        # Don't close in development to keep connection alive
        # db.close()
        print("Done!")

if __name__ == '__main__':
    create_test_user()