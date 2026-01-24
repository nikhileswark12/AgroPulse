from utils.db_connection import get_collection
from config import Config
import logging

logger = logging.getLogger(__name__)

class MarketModel:
    """Model for market data operations"""
    
    def __init__(self):
        self.collection = get_collection(Config.MARKETS_COLLECTION)
    
    def get_all_markets(self, filters=None):
        """Get all markets with optional filters"""
        try:
            query = filters or {}
            markets = self.collection.find(query)
            return list(markets)
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []
    
    def get_market_by_name(self, market_name):
        """Get market by name"""
        try:
            return self.collection.find_one({'mandi_name': market_name})
        except Exception as e:
            logger.error(f"Error fetching market: {e}")
            return None
    
    def get_markets_by_district(self, district):
        """Get all markets in a district"""
        try:
            markets = self.collection.find({'district': district})
            return list(markets)
        except Exception as e:
            logger.error(f"Error fetching markets by district: {e}")
            return []
    
    def get_markets_by_type(self, market_type):
        """Get markets by type (APMC, FPO, Private)"""
        try:
            markets = self.collection.find({'type': market_type})
            return list(markets)
        except Exception as e:
            logger.error(f"Error fetching markets by type: {e}")
            return []
    
    def insert_market(self, market_data):
        """Insert new market"""
        try:
            result = self.collection.insert_one(market_data)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting market: {e}")
            return None
    
    def insert_many_markets(self, markets_list):
        """Insert multiple markets"""
        try:
            result = self.collection.insert_many(markets_list)
            return result.inserted_ids
        except Exception as e:
            logger.error(f"Error inserting markets: {e}")
            return None
    
    def update_market(self, market_name, update_data):
        """Update market information"""
        try:
            result = self.collection.update_one(
                {'mandi_name': market_name},
                {'$set': update_data}
            )
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating market: {e}")
            return 0