from flask import Blueprint, jsonify, current_app
import pandas as pd
import logging
from app import csrf

admin_bp = Blueprint("admin", __name__)
logger = logging.getLogger('startup')

@admin_bp.route("/admin/reload-mandi-data", methods=["POST"])
@csrf.exempt
def reload_mandi_data():
    from flask import request
    
    admin_key = current_app.config.get('ADMIN_KEY', '')
    req_key = request.headers.get('X-Admin-Key')
    
    if not admin_key or req_key != admin_key:
        return jsonify({
            "error": "Forbidden", 
            "message": "Invalid or missing admin key"
        }), 403
        
    try:
        df = pd.read_csv('ml/data/mandi_prices.csv')
        df.columns = [c.lower().strip() for c in df.columns]
        if 'crop' in df.columns:
            df['crop'] = df['crop'].astype(str).str.strip().str.title()
        if 'district' in df.columns:
            df['district'] = df['district'].astype(str).str.strip().str.title()
        if 'state' in df.columns:
            df['state'] = df['state'].astype(str).str.strip().str.title()
            
        current_app.mandi_data = df
        logger.info(f"Mandi data reloaded via admin endpoint: {len(df)} rows")
        
        return jsonify({
            "success": True, 
            "message": "Data reloaded successfully", 
            "rows": len(df)
        })
    except Exception as e:
        logger.warning(f"Failed to reload mandi data: {e}")
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500
