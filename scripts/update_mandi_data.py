import argparse
import pandas as pd
import logging
import os
import sys
import datetime
import requests

# 1. Logger setup
logger = logging.getLogger('agropulse.data_update')
if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

REQUIRED_COLUMNS = ['state', 'district', 'crop', 'modal_price', 'min_price', 'max_price', 'date']
CSV_PATH = 'ml/data/mandi_prices.csv'

# 2. validate_dataframe
def validate_dataframe(df):
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Coerce numeric columns
    for col in ['modal_price', 'min_price', 'max_price']:
        original_nulls = df[col].isnull().sum()
        df[col] = pd.to_numeric(df[col], errors='coerce')
        new_nulls = df[col].isnull().sum()
        if new_nulls > original_nulls:
            logger.warning(f"Coercion to numeric introduced {new_nulls - original_nulls} nulls in {col}")

    # Coerce date
    original_nulls = df['date'].isnull().sum()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    new_nulls = df['date'].isnull().sum()
    if new_nulls > original_nulls:
        logger.warning(f"Coercion to datetime introduced {new_nulls - original_nulls} unparseable rows in date")

    # Clean text columns
    for col in ['state', 'district', 'crop']:
        df[col] = df[col].astype(str).str.strip().str.title()

    # Drop rows where any REQUIRED_COLUMNS value is null after coercion
    before_drop = len(df)
    df = df.dropna(subset=REQUIRED_COLUMNS)
    after_drop = len(df)
    if before_drop > after_drop:
        logger.info(f"Dropped {before_drop - after_drop} rows containing nulls in required columns")

    return df

# 3. merge_data
def merge_data(existing_df, new_df):
    # Ensure existing_df has the right columns to prevent merge issues
    for col in REQUIRED_COLUMNS:
        if col not in existing_df.columns:
            existing_df[col] = pd.NA

    initial_new_len = len(new_df)
    
    existing_df['date'] = pd.to_datetime(existing_df['date'], errors='coerce')
    new_df['date'] = pd.to_datetime(new_df['date'], errors='coerce')

    # Deduplicate new_df internally
    new_df_unique = new_df.drop_duplicates(subset=['state', 'district', 'crop', 'date'], keep='first')
    
    # Find rows in new_df_unique that are NOT in existing_df
    # We use a merge on the exact subset
    merged = new_df_unique.merge(existing_df[['state', 'district', 'crop', 'date']].drop_duplicates(), 
                                 on=['state', 'district', 'crop', 'date'], 
                                 how='left', indicator=True)
                                 
    genuinely_new = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])
    
    new_rows_added = len(genuinely_new)
    duplicates_skipped = initial_new_len - new_rows_added
    
    logger.info(f"Added {new_rows_added} genuinely new rows. Skipped {duplicates_skipped} duplicates.")
    
    combined = pd.concat([existing_df, genuinely_new], ignore_index=True)
    combined = combined.sort_values(by='date', ascending=False)
    
    return combined

# 4. load_from_file
def load_from_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found at path: {path}")
    
    df = pd.read_csv(path)
    return validate_dataframe(df)

# 5. load_from_agmarknet
def load_from_agmarknet():
    # Attempt to fetch data
    try:
        # Example URL for Agmarknet
        response = requests.get('https://agmarknet.gov.in', timeout=10)
        # Check if the response is a CSV
        content_type = response.headers.get('Content-Type', '')
        if 'csv' not in content_type:
            logger.error("AGMARKNET fetch failed. Download data manually from https://agmarknet.gov.in and use --source file --path <downloaded_file.csv> instead")
            return None
        
        # In a real scenario, we'd parse the CSV content here.
        # But since the site usually returns HTML and requires form submissions, it will hit the block above.
        logger.error("AGMARKNET fetch failed. Download data manually from https://agmarknet.gov.in and use --source file --path <downloaded_file.csv> instead")
        return None
    except requests.RequestException as e:
        logger.error("AGMARKNET fetch failed. Download data manually from https://agmarknet.gov.in and use --source file --path <downloaded_file.csv> instead")
        return None

# 6. main
def main():
    parser = argparse.ArgumentParser(description='Update Mandi Data')
    parser.add_argument('--source', required=True, choices=['file', 'agmarknet'], help='Source of the data')
    parser.add_argument('--path', help='Path to the CSV file (required if source is file)')
    parser.add_argument('--dry-run', action='store_true', help='Print summary without writing')
    
    args = parser.parse_args()
    
    if args.source == 'file' and not args.path:
        parser.error("--path is required when --source is file")

    new_df = None
    if args.source == 'file':
        new_df = load_from_file(args.path)
    elif args.source == 'agmarknet':
        new_df = load_from_agmarknet()
        if new_df is None:
            sys.exit(1)

    # Load existing
    if os.path.exists(CSV_PATH):
        existing_df = pd.read_csv(CSV_PATH)
        # Rename columns if needed to match REQUIRED_COLUMNS
        rename_map = {
            'State': 'state',
            'District': 'district',
            'Crops': 'crop',
            'Modal Price': 'modal_price',
            'Min Price': 'min_price',
            'Max Price': 'max_price',
            'Date': 'date'
        }
        existing_df = existing_df.rename(columns=rename_map)
        # Ensure all columns exist
        for col in REQUIRED_COLUMNS:
            if col not in existing_df.columns:
                existing_df[col] = pd.NA
    else:
        existing_df = pd.DataFrame(columns=REQUIRED_COLUMNS)

    merged_df = merge_data(existing_df, new_df)
    
    if args.dry_run:
        logger.info("Dry run complete. Exiting without writing.")
        return

    # Write back
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    merged_df.to_csv(CSV_PATH, index=False)
    logger.info("mandi_prices.csv updated successfully")
    print("Run 'make retrain' to retrain the model on the updated data")
    print("To reflect these changes in the running app immediately, make a POST request to /api/v1/admin/reload-mandi-data")

if __name__ == '__main__':
    main()
