from models.price import PriceModel
from models.market import MarketModel
from utils.helpers import calculate_percentage_change
import logging

logger = logging.getLogger(__name__)

class PriceService:
    """Business logic for price operations"""
    
    def __init__(self):
        self.price_model = PriceModel()
        self.market_model = MarketModel()
    
    def get_current_prices(self, crop, location):
        """Get current prices with market details"""
        try:
            # Get prices
            prices = self.price_model.get_current_prices(crop, location)
            
            if not prices:
                # Try nearby prices if no local prices found
                prices = self.price_model.get_nearby_prices(crop, location)
            
            # Format response
            formatted_prices = []
            for price in prices:
                formatted_prices.append({
                    'mandi': price.get('mandi_name', 'Unknown'),
                    'price': price.get('modal_price', 0),
                    'district': price.get('district', location),
                    'state': price.get('state', ''),
                    'date': price.get('date', ''),
                    'min_price': price.get('min_price', 0),
                    'max_price': price.get('max_price', 0),
                    'type': price.get('type', 'APMC')
                })
            
            # Sort by price (highest first)
            formatted_prices.sort(key=lambda x: x['price'], reverse=True)
            
            return formatted_prices
        
        except Exception as e:
            logger.error(f"Error in get_current_prices: {e}")
            return []
    
    def get_best_price(self, prices):
        """Find best price from list"""
        if not prices:
            return None
        
        return max(prices, key=lambda x: x['price'])
    
    def get_price_statistics(self, crop, location):
        """Get price statistics"""
        try:
            stats = self.price_model.get_average_price(crop, location, days=7)
            
            if stats:
                # Add percentage change
                current_avg = stats['average']
                prev_stats = self.price_model.get_average_price(crop, location, days=14)
                
                if prev_stats:
                    change = calculate_percentage_change(prev_stats['average'], current_avg)
                    stats['change_percent'] = change
                
                return stats
            
            return None
        
        except Exception as e:
            logger.error(f"Error in get_price_statistics: {e}")
            return None