from models.price import PriceModel
from models.predict import PredictionModel
from ml.predict import predict_price
from config import Config
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    """Business logic for price predictions"""
    
    def __init__(self):
        self.price_model = PriceModel()
        self.prediction_model = PredictionModel()
    
    def get_prediction(self, crop, location, days=7):
        """Get price prediction"""
        try:
            # Check for recent prediction (cache)
            recent = self.prediction_model.get_recent_prediction(crop, location, hours=2)
            
            if recent:
                logger.info("Using cached prediction")
                return self.format_prediction(recent)
            
            # Make prediction
            prediction = predict_price(crop, location)
            
            if not prediction or not prediction.get('success'):
                return None
            
            # Save prediction
            prediction_data = {
                'crop': crop,
                'location': location,
                'predicted_prices': prediction.get('predicted_prices', []),
                'trend': prediction.get('trend', 'stable'),
                'optimal_day': 1,
                'confidence': prediction.get('confidence', 'medium'),
                'current_price': prediction.get('predicted_price', 0)
            }
            
            self.prediction_model.save_prediction(prediction_data)
            
            return prediction
        
        except Exception as e:
            logger.error(f"Error in get_prediction: {e}")
            return None
    
    def format_prediction(self, prediction_doc):
        """Format prediction document"""
        return {
            'predictedPrices': prediction_doc.get('predicted_prices', []),
            'trend': prediction_doc.get('trend', 'stable'),
            'optimalDay': prediction_doc.get('optimal_day', 1),
            'confidence': prediction_doc.get('confidence', 0),
            'current_price': prediction_doc.get('current_price', 0)
        }