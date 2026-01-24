from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    """MongoDB database connection handler"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            if self._client is None:
                self._client = MongoClient(Config.MONGODB_URI)
                self._db = self._client[Config.DATABASE_NAME]
                
                # Test connection
                self._client.admin.command('ping')
                logger.info(f"Connected to MongoDB: {Config.DATABASE_NAME}")
                
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_db(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    def get_collection(self, collection_name):
        """Get collection from database"""
        db = self.get_db()
        return db[collection_name]
    
    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")

# Singleton instance
db = Database()

def get_db():
    """Helper function to get database instance"""
    return db.get_db()

def get_collection(collection_name):
    """Helper function to get collection"""
    return db.get_collection(collection_name)