from flask import Blueprint, request, jsonify, session, current_app
from datetime import datetime
from utils.logger import get_logger
from app import limiter
from config import Config
from app import csrf

prediction_bp = Blueprint("prediction", __name__)
logger = get_logger("prediction")

# ML IMPORT
try:
    import ml.predict as ml_predict
    ML_AVAILABLE = True
    logger.info("ML model available")
except Exception as e:
    ML_AVAILABLE = False
    logger.error(f"ML model import failed: {e}")

from utils.db_connection import get_db

# FALLBACK PREDICTION
def fallback_prediction(crop, location, state="Madhya Pradesh"):
    import numpy as np

    base_price = 2000 + np.random.randint(-200, 200)
    predicted_prices = [
        round(base_price + np.random.randint(-40, 120) * i, 2)
        for i in range(1, 8)
    ]

    confidence_margin = 80
    upper = [p + confidence_margin for p in predicted_prices]
    lower = [p - confidence_margin for p in predicted_prices]

    return {
        "success": True,
        "predicted_price": predicted_prices[0],
        "predicted_prices": predicted_prices,
        "upper_bound": upper,
        "lower_bound": lower,
        "recommendation": "WAIT 3 DAYS",
        "expected_gain": f"₹{predicted_prices[-1] - predicted_prices[0]:.0f} / quintal",
        "best_market": f"{location} APMC",
        "trend": "stable",
        "confidence": "medium",
        "model_type": "fallback"
    }

# MAIN PREDICTION API
@prediction_bp.route("/predict", methods=["POST"])
@csrf.exempt
@limiter.limit('30 per hour')
def predict():
    try:
        data = request.get_json()
        crop = data.get("crop")
        location = data.get("location")
        state = data.get("state", "Madhya Pradesh")
        quantity = data.get("quantity", 100)
        district = data.get("district", location)

        user_id = session.get("user_id")
        log_msg = f"Prediction request: crop={crop}, state={state}, district={district}"
        if user_id:
            log_msg += f", user_id={user_id}"
        logger.info(log_msg)

        if not crop or not location:
            return jsonify({
                "success": False,
                "message": "Crop and location are required"
            }), 400

        # ML PREDICTION
        if ML_AVAILABLE:
            try:
                result = ml_predict.predict_price(
                    crop=crop,
                    location=location,
                    state=state,
                    quantity=quantity
                )
            except Exception as e:
                logger.warning(f"ML prediction failed, falling back: {e}")
                result = fallback_prediction(crop, location, state)
        else:
            logger.warning("ML not available, using fallback prediction")
            result = fallback_prediction(crop, location, state)

        # SAVE HISTORY
        if result.get("success") and "user_id" in session:
            try:
                db = get_db()
                db[Config.PREDICTION_HISTORY_COLLECTION].insert_one({
                    "user_id": session.get("user_id"),
                    "crop": crop,
                    "state": state,
                    "district": data.get("district", location),
                    "quantity": data.get("quantity"),
                    "predicted_prices": result.get("predicted_prices", []),
                    "upper_bound": result.get("upper_bound", []),
                    "lower_bound": result.get("lower_bound", []),
                    "recommendation": result.get("recommendation"),
                    "expected_gain": result.get("expected_gain"),
                    "best_market": result.get("best_market"),
                    "confidence": result.get("confidence"),
                    "trend": result.get("trend"),
                    "created_at": datetime.utcnow()
                })
            except Exception as e:
                logger.warning(f"Failed to save prediction history: {e}")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Prediction failed"}), 500

# FETCH HISTORY
@prediction_bp.route("/predict/history", methods=["GET"])
def prediction_history():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    from utils.helpers import get_page, paginated_response
    db = get_db()
    
    page_info = get_page(request.args)
    
    filter_query = {"user_id": session["user_id"]}
    total = db[Config.PREDICTION_HISTORY_COLLECTION].count_documents(filter_query)
    
    projection = {
        '_id': 1, 'crop': 1, 'state': 1, 'district': 1,
        'predicted_prices': 1, 'recommendation': 1,
        'confidence': 1, 'trend': 1, 'created_at': 1
    }

    history = list(
        db[Config.PREDICTION_HISTORY_COLLECTION]
        .find(filter_query, projection)
        .sort("created_at", -1)
        .skip(page_info['skip'])
        .limit(page_info['limit'])
    )

    for h in history:
        h["_id"] = str(h["_id"])
        h["created_at"] = h["created_at"].isoformat()

    return jsonify(paginated_response(history, total, page_info['page'], page_info['per_page'])), 200

# DELETE HISTORY
@prediction_bp.route("/predict/history/<history_id>", methods=["DELETE"])
@csrf.exempt
def delete_prediction(history_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    from bson import ObjectId
    db = get_db()

    result = db[Config.PREDICTION_HISTORY_COLLECTION].delete_one({
        "_id": ObjectId(history_id),
        "user_id": session["user_id"]
    })

    if result.deleted_count:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Not found"}), 404

# MODEL INFO
@prediction_bp.route("/predict/model-info", methods=["GET"])
@prediction_bp.route('/predict/metadata', methods=['GET'])
def model_info():
    try:
        import pandas as pd
        import os
        
        csv_path = os.path.join(
            os.path.dirname(__file__), '..', 'ml', 'data', 'mandi_prices.csv'
        )
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.columns = df.columns.str.strip()
            
            all_states = sorted(df['state'].unique().tolist())
            all_districts = sorted(df['district'].unique().tolist())
            all_crops = sorted(df['crop'].unique().tolist())
            
            state_district_mapping = {}
            for state in all_states:
                districts = df[df['state'] == state]['district'].unique().tolist()
                state_district_mapping[state] = sorted(districts)
            
            logger.info(f"✅ Loaded {len(all_states)} states, {len(all_districts)} districts, {len(all_crops)} crops")
            
            return jsonify({
                "success": True,
                "ml_available": ML_AVAILABLE,
                "n_states": len(all_states),
                "n_districts": len(all_districts),
                "n_crops": len(all_crops),
                "supported_states": all_states,
                "supported_districts": all_districts,
                "supported_crops": all_crops,
                "state_district_mapping": state_district_mapping,
                "sample_states": all_states[:10],
                "sample_districts": all_districts[:15],
                "sample_crops": all_crops[:15]
            }), 200
        else:
            logger.warning("⚠️ CSV not found")
            
            fallback_mapping = {
                "Madhya Pradesh": ["Indore", "Bhopal"],
                "Rajasthan": ["Jaipur", "Chittorgarh"]
            }
            
            return jsonify({
                "success": True,
                "ml_available": False,
                "state_district_mapping": fallback_mapping,
                "supported_states": list(fallback_mapping.keys()),
                "supported_crops": ["Wheat", "Rice"]
            }), 200
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500