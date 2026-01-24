from flask import Blueprint, request, jsonify
from models.market import MarketModel
from utils.helpers import format_response
import logging

logger = logging.getLogger(__name__)

market_bp = Blueprint('market', __name__)
market_model = MarketModel()

@market_bp.route('/markets', methods=['GET'])
def get_markets():
    """Get all markets with optional filters"""
    try:
        district = request.args.get('district')
        market_type = request.args.get('type')
        
        filters = {}
        if district:
            filters['district'] = district
        if market_type:
            filters['type'] = market_type
        
        markets = market_model.get_all_markets(filters)
        
        # Format response
        formatted_markets = []
        for market in markets:
            formatted_markets.append({
                'name': market.get('mandi_name'),
                'district': market.get('district'),
                'state': market.get('state'),
                'type': market.get('type', 'APMC'),
                'contact': market.get('contact', {}),
                'location': market.get('location', {}),
                'crops_accepted': market.get('crops_accepted', [])
            })
        
        return jsonify(format_response(
            True,
            data={'markets': formatted_markets, 'count': len(formatted_markets)}
        ))
    
    except Exception as e:
        logger.error(f"Error in get_markets: {e}")
        return jsonify(format_response(False, errors=[str(e)])), 500

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