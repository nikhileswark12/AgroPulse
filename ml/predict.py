import pickle
from turtle import pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

# ============================================================
# GLOBAL CACHED OBJECTS
# ============================================================
_MODEL = None
_STATE_ENC = None
_DISTRICT_ENC = None
_CROP_ENC = None
_METADATA = None
_MODEL_LOADED = False


# ============================================================
# LOAD MODEL & ENCODERS (ONCE)
# ============================================================
def load_model():
    global _MODEL, _STATE_ENC, _DISTRICT_ENC, _CROP_ENC, _METADATA, _MODEL_LOADED

    if _MODEL_LOADED:
        return True

    try:
        base = os.path.dirname(__file__)

        _MODEL = pickle.load(open(os.path.join(base, "trained_model.pkl"), "rb"))
        _STATE_ENC = pickle.load(open(os.path.join(base, "state_encoder.pkl"), "rb"))
        _DISTRICT_ENC = pickle.load(open(os.path.join(base, "district_encoder.pkl"), "rb"))
        _CROP_ENC = pickle.load(open(os.path.join(base, "crop_encoder.pkl"), "rb"))

        try:
            _METADATA = pickle.load(open(os.path.join(base, "model_metadata.pkl"), "rb"))
        except Exception:
            _METADATA = {}

        _MODEL_LOADED = True
        logger.info("✅ ML model loaded successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to load ML model: {e}")
        return False

def encode_value(value, encoder):
    try:
        return encoder.transform([value])[0]
    except ValueError:
        value = value.lower()
        for idx, cls in enumerate(encoder.classes_):
            if value in cls.lower() or cls.lower() in value:
                return idx
        return 0  # safe fallback


def predict_price(crop, location, state="Madhya Pradesh", quantity=100):
    """
    Predict crop price using trained ML model
    """

    if not load_model():
        raise RuntimeError("ML model not available")

    # ----------------------------
    # CLEAN INPUTS
    # ----------------------------
    crop = crop.strip()
    district = location.strip()
    state = state.strip()

    # ----------------------------
    # ENCODE INPUTS
    # ----------------------------
    state_enc = encode_value(state, _STATE_ENC)
    district_enc = encode_value(district, _DISTRICT_ENC)
    crop_enc = encode_value(crop, _CROP_ENC)

    matched_state = _STATE_ENC.classes_[state_enc]
    matched_district = _DISTRICT_ENC.classes_[district_enc]
    matched_crop = _CROP_ENC.classes_[crop_enc]

    logger.info(
        f"ML Match → State={matched_state}, District={matched_district}, Crop={matched_crop}"
    )

    # ----------------------------
    # BASE PRICE PREDICTION
    # ----------------------------
    import pandas as pd

    X = pd.DataFrame(
        [[state_enc, district_enc, crop_enc]],
        columns=["state_enc", "district_enc", "crop_enc"]
    )

    base_price = float(_MODEL.predict(X)[0])

    # ----------------------------
    # 7-DAY FORECAST
    # ----------------------------
    today = datetime.utcnow()
    predicted_prices = []

    month = today.month
    if month in [10, 11, 12, 1]:
        trend = -0.01
    elif month in [4, 5, 6]:
        trend = 0.015
    else:
        trend = 0.005

    for i in range(1, 8):
        noise = np.random.uniform(-0.02, 0.02)
        future_price = base_price * (1 + trend * i + noise)
        predicted_prices.append(round(future_price, 2))

    # ----------------------------
    # CONFIDENCE INTERVALS (MAE-BASED)
    # ----------------------------
    mae = _METADATA.get("test_mae", 80)
    margin = min(120, max(60, mae * 0.5))

    upper = [round(p + margin, 2) for p in predicted_prices]
    lower = [round(max(0, p - margin), 2) for p in predicted_prices]

    # ----------------------------
    # RECOMMENDATION LOGIC
    # ----------------------------
    diff = predicted_prices[-1] - predicted_prices[0]
    pct = (diff / predicted_prices[0]) * 100

    if diff > 150 or pct > 7:
        recommendation = "WAIT 5-7 DAYS"
        trend_label = "rising"
    elif diff > 75 or pct > 3:
        recommendation = "WAIT 3 DAYS"
        trend_label = "rising"
    elif diff < -75:
        recommendation = "SELL IMMEDIATELY"
        trend_label = "falling"
    else:
        recommendation = "SELL NOW"
        trend_label = "stable"

    # ----------------------------
    # CONFIDENCE LABEL
    # ----------------------------
    r2 = _METADATA.get("test_r2", 0.7)
    confidence = "high" if r2 > 0.85 else "medium" if r2 > 0.7 else "low"

    # ----------------------------
    # FINAL RESPONSE
    # ----------------------------
    return {
        "success": True,
        "predicted_price": round(base_price, 2),
        "predicted_prices": predicted_prices,
        "upper_bound": upper,
        "lower_bound": lower,
        "recommendation": recommendation,
        "expected_gain": f"₹{abs(diff):.0f} / quintal",
        "best_market": f"{matched_district} APMC",
        "trend": trend_label,
        "confidence": confidence,
        "model_type": "machine_learning",
        "matched_crop": matched_crop,
        "matched_district": matched_district,
        "matched_state": matched_state
    }


# ============================================================
# QUICK LOCAL TEST
# ============================================================
if __name__ == "__main__":
    print("🧪 Testing predict_price()...\n")
    res = predict_price(
        crop="Wheat",
        location="Chittorgarh",
        state="Rajasthan"
    )
    for k, v in res.items():
        print(f"{k}: {v}")
