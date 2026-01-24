from models.price import PriceModel
from models.predict import PredictionModel
from ml.predict import PricePredictor
from config import Config
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    """Business logic for price predictions"""
    
    def __init__(self):
        self.price_model = PriceModel()
        self.prediction_model = PredictionModel()
        self.predictor = PricePredictor()
    
    def get_prediction(self, crop, location, days=7):
        """Get price prediction"""
        try:
            # Check for recent prediction (cache)
            recent = self.prediction_model.get_recent_prediction(crop, location, hours=2)
            
            if recent:
                logger.info("Using cached prediction")
                return self.format_prediction(recent)
            
            # Get historical data
            historical = self.price_model.get_historical_prices(
                crop, location, days=Config.HISTORICAL_DAYS
            )
            
            if len(historical) < 10:
                logger.warning(f"Insufficient data for {crop} in {location}")
                return None
            
            # Make prediction
            prediction = self.predictor.predict(historical, days)
            
            if not prediction:
                return None
            
            # Save prediction
            prediction_data = {
                'crop': crop,
                'location': location,
                'predicted_prices': prediction['predictedPrices'],
                'trend': prediction['trend'],
                'optimal_day': prediction['optimalDay'],
                'confidence': prediction['confidence'],
                'current_price': prediction['current_price']
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