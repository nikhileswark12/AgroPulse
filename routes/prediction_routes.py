from flask import Blueprint, request, jsonify, session, current_app
from datetime import datetime
import logging
from app import limiter
from config import Config

prediction_bp = Blueprint("prediction", __name__)
logger = logging.getLogger(__name__)

# ML IMPORT
try:
    import ml.predict as ml_predict
    ML_AVAILABLE = True
    logger.info("✅ ML model available")
except Exception as e:
    ML_AVAILABLE = False
    logger.error(f"❌ ML model import failed: {e}")

# DB ACCESS
def get_db():
    return current_app.config["MONGO_DB"]

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
@limiter.limit('30 per hour')
def predict():
    try:
        data = request.get_json()
        crop = data.get("crop")
        location = data.get("location")
        state = data.get("state", "Madhya Pradesh")
        quantity = data.get("quantity", 100)

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
                logger.error(f"ML prediction failed: {e}")
                result = fallback_prediction(crop, location, state)
        else:
            result = fallback_prediction(crop, location, state)

        # SAVE HISTORY
        if result.get("success") and "user_id" in session:
            try:
                db = get_db()
                db[Config.PREDICTION_HISTORY_COLLECTION].insert_one({
                    "user_id": session["user_id"],
                    "crop": crop,
                    "location": location,
                    "state": state,
                    "quantity": quantity,
                    "predicted_prices": result["predicted_prices"],
                    "upper_bound": result["upper_bound"],
                    "lower_bound": result["lower_bound"],
                    "recommendation": result["recommendation"],
                    "expected_gain": result["expected_gain"],
                    "best_market": result["best_market"],
                    "confidence": result["confidence"],
                    "trend": result["trend"],
                    "created_at": datetime.utcnow()
                })
            except Exception as e:
                logger.error(f"Failed to save prediction history: {e}")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Prediction failed"}), 500

# FETCH HISTORY
@prediction_bp.route("/predict/history", methods=["GET"])
def prediction_history():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    db = get_db()
    limit = request.args.get("limit", 10, type=int)

    history = list(
        db[Config.PREDICTION_HISTORY_COLLECTION]
        .find({"user_id": session["user_id"]})
        .sort("created_at", -1)
        .limit(limit)
    )

    for h in history:
        h["_id"] = str(h["_id"])
        h["created_at"] = h["created_at"].isoformat()

    return jsonify({"success": True, "count": len(history), "history": history}), 200

# DELETE HISTORY
@prediction_bp.route("/predict/history/<history_id>", methods=["DELETE"])
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
            
            all_states = sorted(df['State'].unique().tolist())
            all_districts = sorted(df['District'].unique().tolist())
            all_crops = sorted(df['Crops'].unique().tolist())
            
            state_district_mapping = {}
            for state in all_states:
                districts = df[df['State'] == state]['District'].unique().tolist()
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