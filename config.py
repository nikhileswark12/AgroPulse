import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BaseConfig:
    """Base configuration class with safe defaults"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    ADMIN_KEY = os.environ.get('ADMIN_KEY', '')
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # MongoDB Configuration
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.environ.get('DATABASE_NAME', 'agropulse')
    
    # Collections
    PRICES_COLLECTION = 'prices'
    MARKETS_COLLECTION = 'markets'
    PREDICTIONS_COLLECTION = 'predictions'
    PREDICTION_HISTORY_COLLECTION = 'prediction_history'
    
    # ML Model Configuration
    MODEL_PATH = os.path.join('ml', 'trained_model.pkl')
    SCALER_PATH = os.path.join('ml', 'scaler.pkl')
    
    # Prediction Settings
    PREDICTION_DAYS = 7
    HISTORICAL_DAYS = 90
    
    # Supported Crops
    SUPPORTED_CROPS = [
        'Wheat', 'Rice', 'Soybean', 'Cotton', 
        'Corn', 'Chickpea', 'Mustard', 'Sugarcane',
        'Groundnut', 'Onion'
    ]
    
    # Supported States/Districts
    SUPPORTED_STATES = [
        'Madhya Pradesh', 'Maharashtra', 'Punjab', 
        'Gujarat', 'Rajasthan'
    ]
    
    # API Configuration
    API_PREFIX = '/api'
    
    # CORS Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5000')
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'memory://')
    
    # Logging
    LOG_FILE = os.path.join('logs', 'app.log')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Base URL
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', '')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    MONGO_URI = os.environ.get('MONGO_URI_TEST', 'mongodb://localhost:27017/agropulse_test')


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    
    @classmethod
    def validate(cls):
        secret_key = cls.SECRET_KEY or ""
        if secret_key == "dev-secret-change-in-production" or len(secret_key) < 32:
            raise RuntimeError("Production SECRET_KEY must be explicitly configured and at least 32 characters long")

        from urllib.parse import urlparse

        mongo_uri = cls.MONGO_URI or ""
        parsed_uri = urlparse(mongo_uri)
        if parsed_uri.scheme not in {"mongodb", "mongodb+srv"} or not parsed_uri.hostname:
            raise RuntimeError("Production MONGO_URI must be a valid MongoDB URI")
        if parsed_uri.hostname.lower() in {"localhost", "127.0.0.1", "::1"}:
            raise RuntimeError("MONGO_URI cannot point to localhost in production")


config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Alias Config to BaseConfig for backward compatibility
Config = BaseConfig