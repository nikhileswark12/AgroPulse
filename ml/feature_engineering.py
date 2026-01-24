"""
Feature Engineering for Price Prediction
Extracts meaningful features from historical price data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering for crop price prediction"""
    
    def __init__(self):
        self.feature_names = []
    
    def create_features(self, df):
        """
        Create features from historical price data
        
        Args:
            df: DataFrame with columns ['date', 'modal_price']
            
        Returns:
            DataFrame with engineered features
        """
        try:
            # Make a copy
            df = df.copy()
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            
            # Basic features
            df = self._add_temporal_features(df)
            df = self._add_price_features(df)
            df = self._add_trend_features(df)
            df = self._add_volatility_features(df)
            df = self._add_seasonal_features(df)
            
            # Store feature names
            self.feature_names = [col for col in df.columns if col not in ['date', 'modal_price']]
            
            logger.info(f"Created {len(self.feature_names)} features")
            
            return df
        
        except Exception as e:
            logger.error(f"Error in feature creation: {e}")
            return df
    
    def _add_temporal_features(self, df):
        """Add time-based features"""
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_year'] = df['date'].dt.dayofyear
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['quarter'] = df['date'].dt.quarter
        
        # Days from start (for trend)
        df['days_from_start'] = (df['date'] - df['date'].min()).dt.days
        
        return df
    
    def _add_price_features(self, df):
        """Add price-based features"""
        # Lagged prices
        df['price_lag_1'] = df['modal_price'].shift(1)
        df['price_lag_7'] = df['modal_price'].shift(7)
        df['price_lag_30'] = df['modal_price'].shift(30)
        
        # Moving averages
        df['price_ma_7'] = df['modal_price'].rolling(window=7, min_periods=1).mean()
        df['price_ma_15'] = df['modal_price'].rolling(window=15, min_periods=1).mean()
        df['price_ma_30'] = df['modal_price'].rolling(window=30, min_periods=1).mean()
        
        # Exponential moving averages
        df['price_ema_7'] = df['modal_price'].ewm(span=7, adjust=False).mean()
        df['price_ema_30'] = df['modal_price'].ewm(span=30, adjust=False).mean()
        
        # Price differences
        df['price_diff_1'] = df['modal_price'].diff(1)
        df['price_diff_7'] = df['modal_price'].diff(7)
        
        return df
    
    def _add_trend_features(self, df):
        """Add trend indicators"""
        # Rate of change
        df['price_roc_7'] = df['modal_price'].pct_change(7) * 100
        df['price_roc_30'] = df['modal_price'].pct_change(30) * 100
        
        # Moving average crossovers
        df['ma_cross_7_30'] = (df['price_ma_7'] - df['price_ma_30'])
        
        # Price position relative to moving averages
        df['price_vs_ma7'] = (df['modal_price'] - df['price_ma_7']) / df['price_ma_7'] * 100
        df['price_vs_ma30'] = (df['modal_price'] - df['price_ma_30']) / df['price_ma_30'] * 100
        
        return df
    
    def _add_volatility_features(self, df):
        """Add volatility measures"""
        # Rolling standard deviation
        df['price_std_7'] = df['modal_price'].rolling(window=7, min_periods=1).std()
        df['price_std_30'] = df['modal_price'].rolling(window=30, min_periods=1).std()
        
        # Coefficient of variation
        df['price_cv_7'] = (df['price_std_7'] / df['price_ma_7']) * 100
        df['price_cv_30'] = (df['price_std_30'] / df['price_ma_30']) * 100
        
        # Price range
        df['price_range_7'] = (
            df['modal_price'].rolling(window=7, min_periods=1).max() - 
            df['modal_price'].rolling(window=7, min_periods=1).min()
        )
        
        return df
    
    def _add_seasonal_features(self, df):
        """Add seasonal/cyclical features"""
        # Crop seasons in India
        # Rabi: October-March (Winter crops)
        # Kharif: July-October (Monsoon crops)
        # Zaid: March-July (Summer crops)
        
        def get_season(month):
            if month in [10, 11, 12, 1, 2, 3]:
                return 1  # Rabi
            elif month in [7, 8, 9, 10]:
                return 2  # Kharif
            else:
                return 3  # Zaid
        
        df['crop_season'] = df['month'].apply(get_season)
        
        # Sine/Cosine encoding for month (cyclical)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Day of week encoding (cyclical)
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def get_feature_names(self):
        """Get list of feature names"""
        return self.feature_names
    
    def prepare_for_prediction(self, df, feature_cols):
        """
        Prepare features for model prediction
        
        Args:
            df: DataFrame with features
            feature_cols: List of feature columns to use
            
        Returns:
            numpy array of features
        """
        # Fill any NaN values
        df_filled = df[feature_cols].fillna(method='ffill').fillna(method='bfill').fillna(0)
        return df_filled.values