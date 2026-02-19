"""
AgriSense AI — Data Preprocessing Utilities
=============================================
Shared preprocessing functions for all ML models.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer


def load_and_clean_soil_data(filepath):
    """Load soil sensor data and handle missing values."""
    df = pd.read_csv(filepath)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Impute missing numerics with median (more robust than mean for sensor data)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    imputer = SimpleImputer(strategy="median")
    df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
    
    # Feature engineering
    df["npk_ratio"] = df["nitrogen_mg_kg"] / (df["phosphorus_mg_kg"] + df["potassium_mg_kg"] + 1e-6)
    df["nutrient_total"] = df["nitrogen_mg_kg"] + df["phosphorus_mg_kg"] + df["potassium_mg_kg"]
    df["month"] = df["timestamp"].dt.month
    df["season"] = df["month"].map(get_season)
    
    return df


def load_and_clean_water_data(filepath):
    """Load water quality data and handle missing values."""
    df = pd.read_csv(filepath)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    imputer = SimpleImputer(strategy="median")
    df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
    
    # Feature engineering
    df["tds_turbidity_ratio"] = df["tds_ppm"] / (df["turbidity_ntu"] + 1e-6)
    df["ion_balance"] = df["chloride_mg_l"] + df["sulfate_mg_l"] + df["nitrate_mg_l"]
    df["month"] = df["timestamp"].dt.month
    
    return df


def load_and_clean_weather_data(filepath):
    """Load weather data and compute derived features."""
    df = pd.read_csv(filepath)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Derived features
    df["heat_index"] = compute_heat_index(df["temperature_c"], df["humidity_pct"])
    df["evapotranspiration_est"] = estimate_eto(
        df["temperature_c"], df["humidity_pct"],
        df["solar_radiation_wm2"], df["wind_speed_kmh"]
    )
    df["month"] = df["timestamp"].dt.month
    df["season"] = df["month"].map(get_season)
    
    return df


def load_crop_database(filepath):
    """Load crop reference database."""
    return pd.read_csv(filepath)


def get_season(month):
    """Map month to Indian agricultural season."""
    if month in [6, 7, 8, 9]:
        return "Kharif"  # Monsoon
    elif month in [10, 11, 12, 1, 2]:
        return "Rabi"  # Winter
    else:
        return "Zaid"  # Summer


def compute_heat_index(temp_c, humidity_pct):
    """Simplified heat index calculation."""
    # Steadman's regression
    hi = 0.5 * (temp_c + 61.0 + ((temp_c - 68.0) * 1.2) + (humidity_pct * 0.094))
    return np.round(hi, 1)


def estimate_eto(temp_c, humidity_pct, solar_rad, wind_speed):
    """
    Simplified Penman-Monteith reference evapotranspiration estimate.
    Returns mm/day estimate.
    """
    # Simplified — real implementation would use full FAO-56 equation
    eto = (0.0023 * (temp_c + 17.8) * np.sqrt(abs(solar_rad + 1)) * 
           (1 - humidity_pct / 100) * (1 + 0.01 * wind_speed))
    return np.round(np.clip(eto, 0, 15), 2)


def prepare_features(df, feature_cols, target_col=None, scale=True):
    """
    Prepare feature matrix and optionally target vector.
    
    Returns:
        X: Feature matrix (scaled if requested)
        y: Target vector (if target_col provided)
        scaler: Fitted scaler (if scale=True)
    """
    X = df[feature_cols].values
    
    scaler = None
    if scale:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
    
    if target_col:
        y = df[target_col].values
        return X, y, scaler
    
    return X, scaler


def encode_categorical(df, columns):
    """Encode categorical columns and return encoders."""
    encoders = {}
    for col in columns:
        le = LabelEncoder()
        df[col + "_encoded"] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    return df, encoders


def generate_soil_health_score(row):
    """
    Generate a composite soil health score (0-100) based on multiple parameters.
    
    Scoring breakdown:
    - NPK balance: 30 points
    - pH appropriateness: 20 points
    - Organic matter: 20 points
    - Moisture level: 15 points
    - EC appropriate: 15 points
    """
    score = 0
    
    # NPK balance (30 pts) — ideal: N=60-120, P=30-60, K=40-80
    n, p, k = row["nitrogen_mg_kg"], row["phosphorus_mg_kg"], row["potassium_mg_kg"]
    n_score = max(0, 10 - abs(n - 80) / 8) 
    p_score = max(0, 10 - abs(p - 45) / 5)
    k_score = max(0, 10 - abs(k - 60) / 6)
    score += n_score + p_score + k_score
    
    # pH (20 pts) — ideal: 6.0-7.5
    ph = row["ph"]
    if 6.0 <= ph <= 7.5:
        score += 20
    elif 5.5 <= ph <= 8.0:
        score += 12
    elif 5.0 <= ph <= 8.5:
        score += 5
    
    # Organic matter (20 pts) — ideal: 3-6%
    om = row["organic_matter_pct"]
    if 3.0 <= om <= 6.0:
        score += 20
    elif 2.0 <= om <= 8.0:
        score += 12
    else:
        score += 5
    
    # Moisture (15 pts) — ideal: 20-45%
    m = row["moisture_pct"]
    if 20 <= m <= 45:
        score += 15
    elif 10 <= m <= 60:
        score += 8
    else:
        score += 3
    
    # EC (15 pts) — ideal: 0.5-2.5 mS/cm
    ec = row["ec_mscm"]
    if 0.5 <= ec <= 2.5:
        score += 15
    elif 0.2 <= ec <= 4.0:
        score += 8
    else:
        score += 2
    
    return np.clip(round(score, 1), 0, 100)


def categorize_health_score(score):
    """Map numeric health score to category."""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Poor"
