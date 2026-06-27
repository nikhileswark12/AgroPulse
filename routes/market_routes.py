from flask import Blueprint, request, jsonify
from models.market import MarketModel
from utils.helpers import format_response
import logging

logger = logging.getLogger(__name__)

market_bp = Blueprint('market', __name__)
market_model = MarketModel()

@market_bp.route('/markets', methods=['GET'])
def get_markets():
    """Get all markets with optional filters and pagination"""
    try:
        from utils.helpers import get_page, paginated_response
        district = request.args.get('district')
        market_type = request.args.get('type')
        
        filters = {}
        if district:
            filters['district'] = district
        if market_type:
            filters['type'] = market_type
        
        page_info = get_page(request.args)
        total = market_model.collection.count_documents(filters)
        
        projection = {
            'mandi_name': 1, 'district': 1, 'state': 1, 
            'type': 1, 'crops_accepted': 1, 'timings': 1, '_id': 0
        }
        
        markets_cursor = market_model.collection.find(filters, projection).skip(page_info['skip']).limit(page_info['limit'])
        
        formatted_markets = []
        for market in markets_cursor:
            formatted_markets.append({
                'name': market.get('mandi_name'),
                'district': market.get('district'),
                'state': market.get('state'),
                'type': market.get('type', 'APMC'),
                'crops_accepted': market.get('crops_accepted', []),
                'timings': market.get('timings')
            })
        
        return jsonify(paginated_response(formatted_markets, total, page_info['page'], page_info['per_page']))
    
    except Exception as e:
        logger.error(f"Error in get_markets: {e}")
        return jsonify({"success": False, "errors": [str(e)]}), 500

@market_bp.route('/markets/<district>', methods=['GET'])
def get_markets_by_district(district):
    """Get markets in a specific district"""
    try:
        markets = market_model.get_markets_by_district(district)
        
        formatted_markets = []
        for market in markets:
            formatted_markets.append({
                'name': market.get('mandi_name'),
                'type': market.get('type', 'APMC'),
                'contact': market.get('contact', {}),
                'crops_accepted': market.get('crops_accepted', [])
            })
        
        return jsonify(format_response(
            True,
            data={'markets': formatted_markets, 'count': len(formatted_markets)}
        ))
    
    except Exception as e:
        logger.error(f"Error in get_markets_by_district: {e}")
        return jsonify(format_response(False, errors=[str(e)])), 500