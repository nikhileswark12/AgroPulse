from flask import Blueprint, request, jsonify
import pandas as pd
import os

mandi_bp = Blueprint("mandi", __name__)

# Path to SAME CSV used for ML training
CSV_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "mandi_prices.csv"
)

@mandi_bp.route("/mandi/compare", methods=["GET"])
def compare_mandi_prices():
    crop = request.args.get("crop")

    if not crop:
        return jsonify({
            "success": False,
            "message": "Crop parameter is required"
        }), 400

    try:
        # Load CSV
        df = pd.read_csv(CSV_PATH)

        # Expected columns (adjust names if needed)
        # crop, district, modal_price, market_type
        df.columns = [c.lower().strip() for c in df.columns]

        # Filter by crop
        crop_df = df[df["crop"].str.lower() == crop.lower()]

        if crop_df.empty:
            return jsonify({
                "success": True,
                "markets": []
            })

        markets = []

        for _, row in crop_df.iterrows():
            markets.append({
                "market": row.get("district", "Unknown"),
                "price": int(row.get("modal_price", 0)),
                "type": row.get("market_type", "APMC"),
                "distance": "—"  # optional enhancement later
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
