import logging
import os
from flask import has_app_context, current_app
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


class Database:
    _instance = None
    _client = None
    _db = None
    _connection_key = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _active_config(self):
        if has_app_context():
            return current_app.config
        from config import config_map
        config_name = os.environ.get("FLASK_ENV", "development").lower()
        config_class = config_map.get(config_name, config_map["default"])
        return {key: getattr(config_class, key) for key in dir(config_class) if key.isupper()}

    def connect(self, config=None):
        active_config = config or self._active_config()
        mongo_uri = active_config.get("MONGO_URI")
        database_name = active_config.get("DATABASE_NAME")
        if not mongo_uri or not database_name:
            raise RuntimeError("MongoDB URI and database name must be configured")
        connection_key = (mongo_uri, database_name)
        if self._client is not None and self._connection_key == connection_key:
            try:
                self._client.admin.command("ping")
                return self._db
            except PyMongoError:
                self.close()
        elif self._client is not None:
            self.close()
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=int(active_config.get("MONGO_TIMEOUT_MS", 5000)))
        try:
            client.admin.command("ping")
        except PyMongoError:
            client.close()
            logger.exception("MongoDB connection check failed")
            raise
        self._client = client
        self._db = client[database_name]
        self._connection_key = connection_key
        logger.info("Connected to MongoDB database %s", database_name)
        return self._db

    def get_db(self):
        active_config = self._active_config()
        expected_key = (active_config.get("MONGO_URI"), active_config.get("DATABASE_NAME"))
        if self._db is None or self._connection_key != expected_key:
            return self.connect(active_config)
        return self._db

    def get_collection(self, collection_name):
        return self.get_db()[collection_name]

    def close(self):
        if self._client is not None:
            self._client.close()
        self._client = None
        self._db = None
        self._connection_key = None


db = Database()


def get_db():
    return db.get_db()


def get_collection(collection_name):
    return db.get_collection(collection_name)
