import pandas as pd
import numpy as np
import sys
import os

# Ensure the parent directory is in the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger('data_pipeline')

def main():
    logger.info("Starting data pipeline...")
    
    input_path = 'ml/data/mandi_prices.csv'
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    # 1. Load Data
    logger.info(f"Loading data from {input_path}")
    df = pd.read_csv(input_path)
    
    # Report initial stats
    logger.info(f"Initial shape: {df.shape}")
    logger.info(f"Columns: {df.columns.tolist()}")
    logger.info(f"Data types:\n{df.dtypes}")
    logger.info(f"Null counts:\n{df.isnull().sum()}")

    # 2. Clean Data
    logger.info("Cleaning data...")
    # Standardize column names to snake_case
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Ensure date column exists (from earlier, mandi_prices might not have date. If it doesn't, we can't do time series)
    # Wait, the user asked to parse date to datetime.
    if 'date' not in df.columns:
        logger.warning("No 'date' column found! Falling back to creating dummy dates for time series features.")
        df['date'] = pd.date_range(end=pd.Timestamp.today(), periods=len(df))
        
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Fill null dates with dummy dates
    null_dates = df['date'].isnull()
    if null_dates.any():
        logger.warning(f"Found {null_dates.sum()} null dates, filling with synthetic dates.")
        dummy_dates = pd.date_range(end=pd.Timestamp.today() - pd.Timedelta(days=30), periods=null_dates.sum())
        df.loc[null_dates, 'date'] = dummy_dates
        
    # Fill or drop other nulls
    null_counts = df.isnull().sum()
    if null_counts.any():
        logger.info("Handling null values...")
        # Drop rows missing critical categorical info
        df = df.dropna(subset=['state', 'district', 'crop'])
        
        # Fill missing prices with median or drop. Let's drop since they are the target.
        if 'modal_price' in df.columns:
            df = df.dropna(subset=['modal_price'])
            
        logger.info(f"Dropped rows with missing critical values. New shape: {df.shape}")

    # Remove duplicates
    initial_len = len(df)
    df = df.drop_duplicates()
    if len(df) < initial_len:
        logger.info(f"Dropped {initial_len - len(df)} duplicate rows.")

    # Normalize string columns
    for col in ['state', 'district', 'crop']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # 3. Engineer Features
    logger.info("Engineering features...")
    # Sort by date for time-series features
    df = df.sort_values(by=['state', 'district', 'crop', 'date'])
    
    # Month and day of week
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    
    # Group by location and crop for lag and rolling features
    # Ensure modal_price is numeric
    df['modal_price'] = pd.to_numeric(df['modal_price'], errors='coerce')
    df = df.dropna(subset=['modal_price'])
    
    groups = df.groupby(['state', 'district', 'crop'])
    
    df['price_lag_1'] = groups['modal_price'].shift(1)
    df['price_lag_7'] = groups['modal_price'].shift(7)
    df['price_lag_30'] = groups['modal_price'].shift(30)
    
    df['rolling_mean_7'] = groups['modal_price'].transform(lambda x: x.rolling(7, min_periods=1).mean())
    df['rolling_std_7'] = groups['modal_price'].transform(lambda x: x.rolling(7, min_periods=1).std())
    
    # Price direction: 1 if price increased compared to yesterday, else 0
    df['price_direction'] = (df['modal_price'] > df['price_lag_1']).astype(int)
    
    # Forward fill or drop NAs created by lags. We'll drop NAs to have clean data for training
    # Actually, lag_30 will drop the first 30 days of each crop. We should fill with current price or drop.
    # Let's fill backwards or drop.
    df = df.fillna({
        'price_lag_1': df['modal_price'],
        'price_lag_7': df['modal_price'],
        'price_lag_30': df['modal_price'],
        'rolling_std_7': 0
    })

    # 4. Save processed data
    processed_path = 'ml/data/processed_prices.csv'
    df.to_csv(processed_path, index=False)
    logger.info(f"Saved processed data to {processed_path}. Shape: {df.shape}")

    # 5. Train/Val/Test Split (70/15/15) chronological
    logger.info("Performing chronological 70/15/15 split...")
    df = df.sort_values(by='date')
    
    n = len(df)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)
    
    train_df = df.iloc[:train_end]
    val_df = df.iloc[train_end:val_end]
    test_df = df.iloc[val_end:]
    
    logger.info(f"Train set: {train_df.shape}")
    logger.info(f"Val set: {val_df.shape}")
    logger.info(f"Test set: {test_df.shape}")
    
    train_df.to_csv('ml/data/train.csv', index=False)
    val_df.to_csv('ml/data/val.csv', index=False)
    test_df.to_csv('ml/data/test.csv', index=False)
    
    logger.info("Data pipeline completed successfully.")

if __name__ == '__main__':
    main()
