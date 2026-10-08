"""
AirGuard AI - Feature Engineering for Predictive Air Quality Time-Series Forecasting
Extracts lag features, rolling statistics, rate-of-change derivatives,
and diurnal cyclical encodings.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from datetime import datetime


def extract_features_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame with columns: ['timestamp', 'pm2_5', 'co2', 'voc', 'temperature', 'humidity'],
    computes lag features, rolling statistics, delta rates, and temporal embeddings.
    """
    df = df.copy()
    if not np.issubdtype(df['timestamp'].dtype, np.datetime64):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Time-based cyclic features
    hours = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60.0
    df['sin_hour'] = np.sin(2 * np.pi * hours / 24.0)
    df['cos_hour'] = np.cos(2 * np.pi * hours / 24.0)
    df['day_of_week'] = df['timestamp'].dt.dayofweek

    # Lag features (assuming 1-minute sampling intervals)
    for col in ['pm2_5', 'co2', 'voc', 'temperature', 'humidity']:
        for lag in [1, 5, 15, 30]:
            df[f'{col}_lag_{lag}'] = df[col].shift(lag)

    # Rolling window statistics (5m, 15m, 60m)
    for col in ['pm2_5', 'co2', 'voc']:
        df[f'{col}_roll_mean_5'] = df[col].rolling(window=5, min_periods=1).mean()
        df[f'{col}_roll_std_5'] = df[col].rolling(window=5, min_periods=1).std().fillna(0)
        df[f'{col}_roll_mean_15'] = df[col].rolling(window=15, min_periods=1).mean()
        df[f'{col}_roll_mean_60'] = df[col].rolling(window=60, min_periods=1).mean()
        
        # Rate of change (derivative over 5 mins and 15 mins)
        df[f'{col}_diff_5'] = df[col] - df[col].shift(5)
        df[f'{col}_diff_15'] = df[col] - df[col].shift(15)

    # Cross-sensor interactions
    df['pm_humidity_interaction'] = df['pm2_5'] * (df['humidity'] / 100.0)
    df['voc_temp_interaction'] = df['voc'] * (df['temperature'] / 25.0)

    # Forward fill or backfill any edge NaNs created by lagging
    df = df.bfill().ffill()
    return df


def extract_realtime_feature_vector(
    recent_readings: List[Dict[str, Any]],
    current_time: Optional[datetime] = None
) -> np.ndarray:
    """
    Extracts a single 1D feature vector for real-time inference from the most recent
    series of sensor readings (at least 30-60 points recommended).
    """
    if not recent_readings:
        # Fallback dummy baseline vector
        return np.zeros((1, 35))

    df = pd.DataFrame(recent_readings)
    if 'timestamp' not in df.columns:
        if current_time is None:
            current_time = datetime.now()
        df['timestamp'] = [current_time - pd.Timedelta(minutes=len(df)-1-i) for i in range(len(df))]

    df_feats = extract_features_from_dataframe(df)
    
    # Feature columns excluding timestamp, targets, and raw device metadata
    feature_cols = [
        c for c in df_feats.columns
        if c not in ['timestamp', 'device_id', 'location', 'id', 'aqi', 'aqi_category']
        and not c.startswith('target_')
    ]

    last_row = df_feats.iloc[-1][feature_cols].values.astype(np.float32)
    return last_row.reshape(1, -1), feature_cols
