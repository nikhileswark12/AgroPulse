import bcrypt
from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017/').agropulse
hashed = bcrypt.hashpw(b'newpassword123', bcrypt.gensalt())
db.users.update_one({'email': 'test@example.com'}, {'$set': {'password': hashed, 'verified': True}})
print('Updated password to valid bcrypt hash')
