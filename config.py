import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'agropulse')
    
    # Collections
    PRICES_COLLECTION = 'prices'
    MARKETS_COLLECTION = 'markets'
    PREDICTIONS_COLLECTION = 'predictions'
    
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
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Logging
    LOG_FILE = os.path.join('logs', 'app.log')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')