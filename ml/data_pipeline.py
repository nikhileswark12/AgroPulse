import logging
import os

import pandas as pd

LOGGER = logging.getLogger("agropulse.data_pipeline")
REQUIRED_COLUMNS = {"state", "district", "crop", "modal_price", "date"}


def prepare_temporal_data(data, minimum_unique_dates=30, minimum_dated_records=100):
    frame = data.copy()
    frame.columns = frame.columns.str.strip().str.lower().str.replace(" ", "_")
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError("Temporal training requires columns: " + ", ".join(missing))

    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["modal_price"] = pd.to_numeric(frame["modal_price"], errors="coerce")
    for column in ("state", "district", "crop"):
        frame[column] = frame[column].astype("string").str.strip()
        frame[column] = frame[column].replace("", pd.NA)
    frame = frame.dropna(subset=["date", "modal_price", "state", "district", "crop"])
    frame = frame[frame["modal_price"].gt(0)].copy()
    frame = frame.drop_duplicates(subset=["state", "district", "crop", "date", "modal_price"])
    unique_dates = int(frame["date"].dt.normalize().nunique())
    if len(frame) < minimum_dated_records or unique_dates < minimum_unique_dates:
        raise ValueError(
            "Insufficient dated market observations for time-series processing: "
            f"{len(frame)} valid dated rows across {unique_dates} dates; require at least "
            f"{minimum_dated_records} rows across {minimum_unique_dates} dates. "
            "Refresh the source data; synthetic dates are not created."
        )
    return frame.sort_values(["date", "state", "district", "crop"]).reset_index(drop=True)


def main():
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    input_path = os.environ.get("AGROPULSE_MARKET_DATA", "ml/data/mandi_prices.csv")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Market data file not found: {input_path}")
    frame = prepare_temporal_data(pd.read_csv(input_path))
    os.makedirs("ml/data", exist_ok=True)
    output_path = "ml/data/processed_prices.csv"
    frame.to_csv(output_path, index=False)
    LOGGER.info("Saved %s valid dated observations to %s", len(frame), output_path)


if __name__ == "__main__":
    main()
