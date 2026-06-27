from flask import Blueprint, request, jsonify
from services.price_service import PriceService
from services.prediction_service import PredictionService
from services.recommendation_service import RecommendationService
from utils.validators import validate_price_request
from utils.helpers import format_response
import logging
from app import csrf

logger = logging.getLogger(__name__)

price_bp = Blueprint('price', __name__)

price_service = PriceService()
prediction_service = PredictionService()
recommendation_service = RecommendationService()

@price_bp.route('/prices', methods=['POST'])
@csrf.exempt
def get_prices():
    """Get current prices, prediction, and recommendation"""
    try:
        data = request.get_json()
        
        # Validate input
        valid, errors = validate_price_request(data)
        if not valid:
            return jsonify(format_response(False, errors=errors)), 400
        
        crop = data.get('crop')
        location = data.get('location')
        quantity = data.get('quantity')
        
        # Get current prices
        current_prices = price_service.get_current_prices(crop, location)
        
        if not current_prices:
            return jsonify(format_response(
                False,
                message=f"No price data found for {crop} in {location}"
            )), 404
        
        # Get prediction
        prediction = prediction_service.get_prediction(crop, location, days=7)
        
        # Generate recommendation
        recommendation = recommendation_service.generate_recommendation(
            current_prices, prediction
        )
        
        # Calculate total gain if quantity provided
        if quantity:
            total_gain = recommendation_service.calculate_total_gain(
                recommendation, float(quantity)
            )
            recommendation['totalGain'] = total_gain
        
        # Get price statistics
        stats = price_service.get_price_statistics(crop, location)
        
        response_data = {
            'currentPrices': current_prices[:5],  # Top 5 prices
            'prediction': prediction,
            'recommendation': recommendation,
            'statistics': stats
        }
        
        return jsonify(format_response(True, data=response_data))
    
    except Exception as e:
        logger.error(f"Error in get_prices: {e}")
        return jsonify(format_response(
            False,
            message="Internal server error",
            errors=[str(e)]
        )), 500

@price_bp.route('/prices/current', methods=['GET'])
def get_current_prices_only():
    """Get only current prices"""
    try:
        crop = request.args.get('crop')
        location = request.args.get('location')
        
        if not crop or not location:
            return jsonify(format_response(
                False,
                errors=["Crop and location are required"]
            )), 400
        from utils.helpers import get_page, paginated_response
        page_info = get_page(request.args)
        
        filter_query = {'crop': {'$regex': f'^{crop}$', '$options': 'i'}}
        if location:
            filter_query['district'] = {'$regex': f'^{location}$', '$options': 'i'}
            
        total = price_service.price_model.collection.count_documents(filter_query)
        
        projection = {
            'crop': 1, 'mandi_name': 1, 'district': 1, 'state': 1, 
            'modal_price': 1, 'min_price': 1, 'max_price': 1, 'date': 1, '_id': 0
        }
        
        prices_cursor = price_service.price_model.collection.find(filter_query, projection).sort('date', -1).skip(page_info['skip']).limit(page_info['limit'])
        
        formatted_prices = []
        for price in prices_cursor:
            formatted_prices.append({
                'mandi': price.get('mandi_name', 'Unknown'),
                'price': price.get('modal_price', 0),
                'district': price.get('district', location),
                'state': price.get('state', ''),
                'date': price.get('date', ''),
                'min_price': price.get('min_price', 0),
                'max_price': price.get('max_price', 0),
                'crop': price.get('crop', crop)
            })
        
        return jsonify(paginated_response(formatted_prices, total, page_info['page'], page_info['per_page']))
    
    except Exception as e:
        logger.error(f"Error in get_current_prices_only: {e}")
        return jsonify(format_response(False, errors=[str(e)])), 500

@price_bp.route('/prices/statistics', methods=['GET'])
def get_statistics():
    """Get price statistics"""
    try:
        crop = request.args.get('crop')
        location = request.args.get('location')
        
        if not crop or not location:
            return jsonify(format_response(
                False,
                errors=["Crop and location are required"]
            )), 400
        
        stats = price_service.get_price_statistics(crop, location)
        
        if not stats:
            return jsonify(format_response(
                False,
                message="No statistics available"
            )), 404
        
        return jsonify(format_response(True, data=stats))
    
    except Exception as e:
        logger.error(f"Error in get_statistics: {e}")
        return jsonify(format_response(False, errors=[str(e)])), 500