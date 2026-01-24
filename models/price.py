from utils.db_connection import get_collection
from config import Config
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PriceModel:
    """Model for price data operations"""
    
    def __init__(self):
        self.collection = get_collection(Config.PRICES_COLLECTION)
    
    def get_current_prices(self, crop, district, days=2):
        """Get current prices for a crop in a district"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            prices = self.collection.find({
                'crop': crop,
                'district': district,
                'date': {'$gte': cutoff_date}
            }).sort('date', -1)
            
            return list(prices)
        
        except Exception as e:
            logger.error(f"Error fetching current prices: {e}")
            return []
    
    def get_nearby_prices(self, crop, district, radius_km=50):
        """Get prices from nearby markets"""
        try:
            # For now, we'll get prices from the same state
            # In production, implement geospatial queries
            
            cutoff_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
            
            prices = self.collection.find({
                'crop': crop,
                'date': {'$gte': cutoff_date}
            }).sort('date', -1).limit(10)
            
            return list(prices)
        
        except Exception as e:
            logger.error(f"Error fetching nearby prices: {e}")
            return []
    
    def get_historical_prices(self, crop, district, days=90):
        """Get historical prices for ML model"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            prices = self.collection.find({
                'crop': crop,
                'district': district,
                'date': {'$gte': start_date, '$lte': end_date}
            }).sort('date', 1)
            
            return list(prices)
        
        except Exception as e:
            logger.error(f"Error fetching historical prices: {e}")
            return []
    
    def get_price_by_id(self, price_id):
        """Get single price record by ID"""
        try:
            from bson.objectid import ObjectId
            return self.collection.find_one({'_id': ObjectId(price_id)})
        except Exception as e:
            logger.error(f"Error fetching price by ID: {e}")
            return None
    
    def insert_price(self, price_data):
        """Insert new price record"""
        try:
            price_data['created_at'] = datetime.now()
            result = self.collection.insert_one(price_data)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting price: {e}")
            return None
    
    def insert_many_prices(self, prices_list):
        """Insert multiple price records"""
        try:
            for price in prices_list:
                price['created_at'] = datetime.now()
            
            result = self.collection.insert_many(prices_list)
            return result.inserted_ids
        except Exception as e:
            logger.error(f"Error inserting prices: {e}")
            return None
    
    def get_average_price(self, crop, district, days=7):
        """Get average price for last N days"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            pipeline = [
                {
                    '$match': {
                        'crop': crop,
                        'district': district,
                        'date': {'$gte': start_date}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'avg_price': {'$avg': '$modal_price'},
                        'min_price': {'$min': '$modal_price'},
                        'max_price': {'$max': '$modal_price'}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result:
                return {
                    'average': round(result[0]['avg_price'], 2),
                    'minimum': result[0]['min_price'],
                    'maximum': result[0]['max_price']
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error calculating average price: {e}")
            return None