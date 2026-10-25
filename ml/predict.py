import logging
import os
from datetime import date, datetime, timedelta

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

_MODEL = None
_STATE_ENC = None
_DISTRICT_ENC = None
_CROP_ENC = None
_METADATA = {}
_MODEL_LOADED = False
_MODEL_PATH_LOADED = None
_MODEL_MTIME = None


def _model_path():
    configured_path = os.environ.get("AGROPULSE_MODEL_PATH")
    if configured_path:
        return os.path.abspath(configured_path)
    return os.path.join(os.path.dirname(__file__), "model_bundle.joblib")


def load_model():
    global _MODEL, _STATE_ENC, _DISTRICT_ENC, _CROP_ENC
    global _METADATA, _MODEL_LOADED, _MODEL_PATH_LOADED, _MODEL_MTIME

    path = _model_path()
    try:
        modified = os.path.getmtime(path)
        if _MODEL_LOADED and _MODEL_PATH_LOADED == path and _MODEL_MTIME == modified:
            return True
        bundle = joblib.load(path)
        if not isinstance(bundle, dict) or bundle.get("format_version") != 1:
            raise ValueError("Unsupported model bundle format")
        model = bundle.get("model")
        encoders = bundle.get("encoders")
        feature_cols = bundle.get("feature_cols")
        metadata = bundle.get("metadata")
        if not model or not isinstance(encoders, dict) or not isinstance(metadata, dict):
            raise ValueError("Model bundle is incomplete")
        if feature_cols != ["state_enc", "district_enc", "crop_enc"]:
            raise ValueError("Model feature schema is unsupported")
        if not all(key in encoders for key in ("state", "district", "crop")):
            raise ValueError("Model category encoders are missing")
        _MODEL = model
        _STATE_ENC = encoders["state"]
        _DISTRICT_ENC = encoders["district"]
        _CROP_ENC = encoders["crop"]
        _METADATA = metadata
        _MODEL_LOADED = True
        _MODEL_PATH_LOADED = path
        _MODEL_MTIME = modified
        logger.info("AgroPulse model bundle loaded")
        return True
    except FileNotFoundError:
        logger.warning("AgroPulse model bundle is missing at %s", path)
    except Exception as exc:
        logger.error("AgroPulse model bundle could not be loaded: %s", exc)
    _MODEL_LOADED = False
    _MODEL = None
    _STATE_ENC = None
    _DISTRICT_ENC = None
    _CROP_ENC = None
    _METADATA = {}
    return False


def encode_value(value, encoder):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Crop, district, and state must be non-empty strings")
    normalized = value.strip().casefold()
    for index, category in enumerate(encoder.classes_):
        if normalized == str(category).strip().casefold():
            return index
    raise ValueError(f"Unsupported category: {value}")


def predict_price(crop, location, state="Madhya Pradesh", quantity=100):
    if not load_model():
        raise RuntimeError("ML model bundle is not available")

    state_enc = encode_value(state, _STATE_ENC)
    district_enc = encode_value(location, _DISTRICT_ENC)
    crop_enc = encode_value(crop, _CROP_ENC)
    features = pd.DataFrame(
        [[state_enc, district_enc, crop_enc]],
        columns=["state_enc", "district_enc", "crop_enc"]
    )
    base_price = float(_MODEL.predict(features)[0])
    if not np.isfinite(base_price) or base_price <= 0:
        raise RuntimeError("Model returned an invalid price estimate")

    today = date.today()
    forecast_dates = [(today + timedelta(days=offset)).isoformat() for offset in range(1, 8)]
    predicted_prices = [round(base_price, 2)] * 7

    mae = _METADATA.get("test_mae")
    if isinstance(mae, (int, float)) and np.isfinite(mae) and mae >= 0:
        upper = [round(base_price + float(mae), 2)] * 7
        lower = [round(max(0, base_price - float(mae)), 2)] * 7
    else:
        upper = []
        lower = []

    return {
        "success": True,
        "predicted_price": round(base_price, 2),
        "predicted_prices": predicted_prices,
        "forecast_dates": forecast_dates,
        "upper_bound": upper,
        "lower_bound": lower,
        "recommendation": "INSUFFICIENT TEMPORAL DATA",
        "expected_gain": "Unavailable",
        "best_market": f"{location.strip()} APMC",
        "trend": "unknown",
        "confidence": "low",
        "model_type": "cross_sectional_price_baseline_not_time_series_forecast",
        "temporal_forecast_supported": False,
        "matched_crop": str(_CROP_ENC.classes_[crop_enc]),
        "matched_district": str(_DISTRICT_ENC.classes_[district_enc]),
        "matched_state": str(_STATE_ENC.classes_[state_enc])
    }


if __name__ == "__main__":
    print("Testing the AgroPulse model bundle")
    print(predict_price(crop="Wheat", location="Chittorgarh", state="Rajasthan"))
