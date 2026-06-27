import bcrypt
from utils.db_connection import get_db

db = get_db()
hashed = bcrypt.hashpw(b'newpassword123', bcrypt.gensalt())
db.users.update_one({'email': 'test@example.com'}, {'$set': {'password': hashed, 'verified': True}})
print('Updated password to valid bcrypt hash')
