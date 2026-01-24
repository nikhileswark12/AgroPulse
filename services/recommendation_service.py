import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    """Business logic for generating recommendations"""
    
    def generate_recommendation(self, current_prices, prediction):
        """Generate sell/wait recommendation"""
        try:
            if not current_prices or not prediction:
                return self.default_recommendation()
            
            # Get average current price
            avg_current = sum(p['price'] for p in current_prices) / len(current_prices)
            
            # Get predicted prices
            predicted_prices = prediction.get('predictedPrices', [])
            
            if not predicted_prices:
                return self.default_recommendation()
            
            # Get maximum predicted price
            max_predicted = max(p['price'] for p in predicted_prices)
            optimal_day = prediction.get('optimalDay', 1)
            
            # Calculate potential gain
            potential_gain = max_predicted - avg_current
            gain_percent = (potential_gain / avg_current) * 100
            
            # Get best current market
            best_market = max(current_prices, key=lambda x: x['price'])
            
            # Decision logic
            if gain_percent > 5:  # If gain > 5%
                action = 'WAIT'
                message = f"Wait {optimal_day} days. Price expected to rise by ₹{potential_gain:.0f} ({gain_percent:.1f}%)"
                confidence = 'HIGH' if prediction.get('confidence', 0) > 0.75 else 'MEDIUM'
            elif gain_percent > 2:  # If gain 2-5%
                action = 'WAIT'
                message = f"Consider waiting {optimal_day} days for ₹{potential_gain:.0f} gain"
                confidence = 'MEDIUM'
            else:
                action = 'SELL NOW'
                message = f"Current prices are good. Sell at {best_market['mandi']}"
                confidence = 'HIGH'
            
            return {
                'action': action,
                'message': message,
                'confidence': confidence,
                'expectedGain': round(potential_gain, 2),
                'gainPercent': round(gain_percent, 2),
                'bestMarket': best_market['mandi'],
                'bestPrice': best_market['price'],
                'optimalDay': optimal_day,
                'recommendedDate': predicted_prices[optimal_day - 1]['date'] if optimal_day <= len(predicted_prices) else None
            }
        
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return self.default_recommendation()
    
    def default_recommendation(self):
        """Default recommendation when data is insufficient"""
        return {
            'action': 'INSUFFICIENT DATA',
            'message': 'Not enough data to make a recommendation',
            'confidence': 'LOW',
            'expectedGain': 0,
            'gainPercent': 0
        }
    
    def calculate_total_gain(self, recommendation, quantity):
        """Calculate total gain for given quantity"""
        if not quantity or recommendation.get('action') == 'INSUFFICIENT DATA':
            return None
        
        expected_gain_per_quintal = recommendation.get('expectedGain', 0)
        total_gain = expected_gain_per_quintal * quantity
        
        return {
            'perQuintal': expected_gain_per_quintal,
            'total': round(total_gain, 2),
            'quantity': quantity
        }