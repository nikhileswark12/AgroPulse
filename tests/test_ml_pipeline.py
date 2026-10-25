import joblib
import numpy as np
import pandas as pd
import pytest

from ml.data_pipeline import prepare_temporal_data
from ml.train_model import prepare_training_data, train_and_save_model


def sample_prices():
    rows = []
    states = ["Gujarat", "Punjab"]
    districts = ["Amreli", "Ludhiana"]
    crops = ["Wheat", "Cotton"]
    for index in range(40):
        rows.append({
            "state": states[index % 2],
            "district": districts[index % 2],
            "crop": crops[(index // 2) % 2],
            "modal_price": 1800 + index * 17,
            "date": ""
        })
    return pd.DataFrame(rows)


def test_training_data_discards_invalid_prices_and_exact_duplicates():
    data = sample_prices()
    data.loc[0, "modal_price"] = np.nan
    data.loc[1, "modal_price"] = -10
    prepared = prepare_training_data(data)
    assert len(prepared) < len(data)
    assert prepared["modal_price"].gt(0).all()
    assert not prepared.duplicated(["state", "district", "crop", "modal_price"]).any()


def test_training_saves_one_versioned_model_bundle(tmp_path):
    data_path = tmp_path / "prices.csv"
    output_path = tmp_path / "model_bundle.joblib"
    sample_prices().to_csv(data_path, index=False)

    metadata = train_and_save_model(str(data_path), str(output_path))
    bundle = joblib.load(output_path)

    assert bundle["format_version"] == 1
    assert bundle["feature_cols"] == ["state_enc", "district_enc", "crop_enc"]
    assert metadata["temporal_forecast_supported"] is False
    assert metadata["date_coverage"]["dated_records"] == 0
    assert metadata["test_mae"] >= 0


def test_training_rejects_too_few_valid_rows():
    with pytest.raises(ValueError, match="At least 10 valid price records"):
        prepare_training_data(sample_prices().head(5))


def test_temporal_pipeline_rejects_missing_dates_without_synthesizing_them():
    with pytest.raises(ValueError, match="synthetic dates are not created"):
        prepare_temporal_data(sample_prices())


def test_temporal_pipeline_accepts_sufficient_real_date_coverage():
    data = sample_prices().copy()
    data["date"] = [pd.Timestamp("2024-01-01") + pd.Timedelta(days=index) for index in range(len(data))]
    prepared = prepare_temporal_data(data, minimum_dated_records=30)
    assert prepared["date"].is_monotonic_increasing
    assert prepared["date"].dt.normalize().nunique() == 40


def test_predict_uses_bundle_and_does_not_invent_daily_trend(tmp_path, monkeypatch):
    from ml import predict

    data_path = tmp_path / "prices.csv"
    model_path = tmp_path / "model_bundle.joblib"
    sample_prices().to_csv(data_path, index=False)
    train_and_save_model(str(data_path), str(model_path))
    monkeypatch.setenv("AGROPULSE_MODEL_PATH", str(model_path))
    monkeypatch.setattr(predict, "_MODEL_LOADED", False)

    result = predict.predict_price("Wheat", "Amreli", "Gujarat")

    assert len(result["predicted_prices"]) == 7
    assert len(set(result["predicted_prices"])) == 1
    assert result["trend"] == "unknown"
    assert result["recommendation"] == "INSUFFICIENT TEMPORAL DATA"
    assert result["temporal_forecast_supported"] is False
    assert result["model_type"] == "cross_sectional_price_baseline_not_time_series_forecast"
