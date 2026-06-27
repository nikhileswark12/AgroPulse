from flask import Blueprint, request, jsonify, current_app
from utils.helpers import calculate_distance
import os

mandi_bp = Blueprint("mandi", __name__)

def get_user_coords(req):
    try:
        lat = req.args.get('lat', type=float)
        lon = req.args.get('lon', type=float)
        return lat, lon
    except:
        return None, None

@mandi_bp.route("/mandi/compare", methods=["GET"])
def compare_mandi_prices():
    crop = request.args.get("crop")

    if not crop:
        return jsonify({
            "success": False,
            "message": "Crop parameter is required"
        }), 400

    try:
        df = current_app.mandi_data
        
        if df is None:
            return jsonify({
                "success": False, 
                "error": "Market data unavailable"
            }), 503

        # Filter by crop
        crop_df = df[df["crop"].str.lower() == crop.lower()]

        if crop_df.empty:
            return jsonify({
                "success": True,
                "markets": []
            })

        user_lat, user_lon = get_user_coords(request)
        markets = []

        for _, row in crop_df.iterrows():
            dist_val = "—"
            district = row.get("district", "").strip().title()
            if user_lat is not None and user_lon is not None and hasattr(current_app, 'district_coords'):
                coords = current_app.district_coords.get(district)
                if coords and 'lat' in coords and 'lon' in coords:
                    dist_km = calculate_distance(user_lat, user_lon, coords['lat'], coords['lon'])
                    dist_val = f"{dist_km} km"

            markets.append({
                "market": row.get("district", "Unknown"),
                "price": int(row.get("modal_price", 0)),
                "type": row.get("market_type", "APMC"),
                "distance": dist_val
            })

        return jsonify({
            "success": True,
            "markets": markets
        })

    except Exception as e:
        print("❌ Mandi API Error:", e)
        return jsonify({
            "success": False,
            "message": "Failed to load mandi prices"
        }), 500
