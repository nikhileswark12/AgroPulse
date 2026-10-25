import argparse
import logging
import os
import tempfile
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

LOGGER = logging.getLogger("agropulse.training")
FEATURE_COLUMNS = ["state_enc", "district_enc", "crop_enc"]
REQUIRED_COLUMNS = ["state", "district", "crop", "modal_price"]


def prepare_training_data(data):
    missing = sorted(set(REQUIRED_COLUMNS) - set(data.columns.str.strip().str.lower()))
    if missing:
        raise ValueError("Training data is missing required columns: " + ", ".join(missing))

    frame = data.copy()
    frame.columns = frame.columns.str.strip().str.lower()
    for column in ("state", "district", "crop"):
        frame[column] = frame[column].astype("string").str.strip()
        frame[column] = frame[column].replace("", pd.NA)
    frame["modal_price"] = pd.to_numeric(frame["modal_price"], errors="coerce")
    frame = frame.dropna(subset=REQUIRED_COLUMNS)
    frame = frame[np.isfinite(frame["modal_price"]) & (frame["modal_price"] > 0)].copy()
    for column in ("state", "district", "crop"):
        frame[column] = frame[column].astype(str)
    frame = frame.drop_duplicates(subset=["state", "district", "crop", "modal_price"])
    if len(frame) < 10:
        raise ValueError(
            f"At least 10 valid price records are required; found {len(frame)}. "
            "No synthetic dates or prices are generated."
        )
    return frame.reset_index(drop=True)


def train_and_save_model(data_path="ml/data/mandi_prices.csv", output_path="ml/model_bundle.joblib"):
    data = pd.read_csv(data_path)
    frame = prepare_training_data(data)

    encoders = {}
    for column in ("state", "district", "crop"):
        encoder = LabelEncoder()
        frame[f"{column}_enc"] = encoder.fit_transform(frame[column])
        encoders[column] = encoder

    features = frame[FEATURE_COLUMNS]
    target = frame["modal_price"]
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, shuffle=True
    )
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=1
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    test_mae = float(mean_absolute_error(y_test, predictions))
    test_rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
    test_r2 = float(r2_score(y_test, predictions)) if len(y_test) >= 2 else None
    if test_r2 is not None and not np.isfinite(test_r2):
        test_r2 = None

    date_coverage = {"dated_records": 0, "unique_dates": 0, "latest_date": None}
    if "date" in data.columns:
        parsed_dates = pd.to_datetime(data["date"], errors="coerce").dropna()
        date_coverage = {
            "dated_records": int(parsed_dates.shape[0]),
            "unique_dates": int(parsed_dates.dt.normalize().nunique()),
            "latest_date": parsed_dates.max().date().isoformat() if not parsed_dates.empty else None
        }

    metadata = {
        "format_version": 1,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(frame)),
        "n_states": int(frame["state"].nunique()),
        "n_districts": int(frame["district"].nunique()),
        "n_crops": int(frame["crop"].nunique()),
        "feature_cols": FEATURE_COLUMNS,
        "test_mae": test_mae,
        "test_rmse": test_rmse,
        "test_r2": test_r2,
        "evaluation_method": "random_holdout_cross_sectional",
        "temporal_forecast_supported": False,
        "date_coverage": date_coverage,
        "supported_crops": sorted(encoders["crop"].classes_.tolist()),
        "supported_states": sorted(encoders["state"].classes_.tolist()),
        "supported_districts": sorted(encoders["district"].classes_.tolist())
    }
    bundle = {
        "format_version": 1,
        "model": model,
        "encoders": encoders,
        "feature_cols": FEATURE_COLUMNS,
        "metadata": metadata
    }

    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fd, temporary_path = tempfile.mkstemp(prefix=".model-bundle-", suffix=".joblib", dir=os.path.dirname(output_path))
    os.close(fd)
    try:
        joblib.dump(bundle, temporary_path)
        os.replace(temporary_path, output_path)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)

    LOGGER.info(
        "Saved cross-sectional baseline model to %s using %s valid records; test MAE %.2f",
        output_path, len(frame), test_mae
    )
    if date_coverage["dated_records"] < len(frame) or date_coverage["unique_dates"] < 30:
        LOGGER.warning(
            "Source data has limited date coverage (%s dated records across %s dates). "
            "The saved model is a cross-sectional baseline, not a time-series forecast.",
            date_coverage["dated_records"], date_coverage["unique_dates"]
        )
    return metadata


def main():
    parser = argparse.ArgumentParser(description="Train the AgroPulse cross-sectional price baseline.")
    parser.add_argument("--data", default="ml/data/mandi_prices.csv")
    parser.add_argument("--output", default="ml/model_bundle.joblib")
    args = parser.parse_args()
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    metadata = train_and_save_model(args.data, args.output)
    print(
        "Training complete: "
        f"samples={metadata['n_samples']}, test_mae={metadata['test_mae']:.2f}, "
        f"dated_records={metadata['date_coverage']['dated_records']}, "
        f"unique_dates={metadata['date_coverage']['unique_dates']}"
    )


if __name__ == "__main__":
    main()
