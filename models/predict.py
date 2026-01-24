from utils.db_connection import get_collection
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PredictionModel:
    """Model for storing and retrieving ML predictions"""
    
    def __init__(self):
        self.collection = get_collection(Config.PREDICTIONS_COLLECTION)
    
    def save_prediction(self, prediction_data):
        """Save ML prediction to database"""
        try:
            prediction_data['created_at'] = datetime.now()
            result = self.collection.insert_one(prediction_data)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return None
    
    def get_recent_prediction(self, crop, district, hours=2):
        """Get recent prediction if exists (within last N hours)"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            prediction = self.collection.find_one({
                'crop': crop,
                'location': district,
                'created_at': {'$gte': cutoff_time}
            }, sort=[('created_at', -1)])
            
            return prediction
        except Exception as e:
            logger.error(f"Error fetching recent prediction: {e}")
            return None
    
    def get_prediction_history(self, crop, district, limit=10):
        """Get prediction history"""
        try:
            predictions = self.collection.find({
                'crop': crop,
                'location': district
            }).sort('created_at', -1).limit(limit)
            
            return list(predictions)
        except Exception as e:
            logger.error(f"Error fetching prediction history: {e}")
            return []