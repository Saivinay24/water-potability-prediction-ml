"""
AgriSense AI — Yield Prediction Model
=======================================
Gradient Boosting regression model that predicts crop yield (tons/hectare)
based on soil health, weather conditions, and irrigation data.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.utils.preprocessing import (
    load_and_clean_soil_data, load_and_clean_weather_data,
    load_crop_database, generate_soil_health_score
)
from models.utils.evaluation import evaluate_regressor, save_metrics, save_predictions

MODEL_NAME = "Yield Predictor"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def create_yield_dataset(soil_path=None, weather_path=None, crop_path=None):
    """
    Create a yield prediction dataset by combining soil health, weather,
    and crop data with simulated yield outcomes.
    """
    if soil_path is None:
        soil_path = os.path.join(PROJECT_ROOT, "data", "raw", "soil_sensors.csv")
    if weather_path is None:
        weather_path = os.path.join(PROJECT_ROOT, "data", "raw", "weather_data.csv")
    if crop_path is None:
        crop_path = os.path.join(PROJECT_ROOT, "data", "raw", "crop_database.csv")
    
    soil_df = load_and_clean_soil_data(soil_path)
    weather_df = load_and_clean_weather_data(weather_path)
    crop_db = load_crop_database(crop_path)
    
    # Compute soil health scores
    soil_df["health_score"] = soil_df.apply(generate_soil_health_score, axis=1)
    
    # Assign crops to zones
    np.random.seed(42)
    zone_crops = {}
    crop_list = crop_db["crop_name"].values
    for i, zone in enumerate(soil_df["zone_id"].unique()):
        zone_crops[zone] = crop_list[i % len(crop_list)]
    soil_df["crop"] = soil_df["zone_id"].map(zone_crops)
    
    # Merge crop expected yields
    soil_df = soil_df.merge(
        crop_db[["crop_name", "expected_yield_tons_per_ha", "water_requirement_mm"]],
        left_on="crop", right_on="crop_name", how="left"
    ).drop("crop_name", axis=1)
    
    # Aggregate weather by month
    weather_df["year_month"] = weather_df["timestamp"].dt.to_period("M")
    monthly_weather = weather_df.groupby("year_month").agg({
        "temperature_c": "mean",
        "humidity_pct": "mean",
        "rainfall_mm": "sum",
        "solar_radiation_wm2": "mean",
    }).reset_index()
    
    soil_df["year_month"] = soil_df["timestamp"].dt.to_period("M")
    merged = soil_df.merge(monthly_weather, on="year_month", how="left", suffixes=("_soil", "_weather"))
    merged = merged.dropna(subset=["temperature_c_weather"])
    
    # Simulate yield based on health, weather, and randomness
    # Yield = base_yield * health_factor * weather_factor * noise
    merged["health_factor"] = merged["health_score"] / 70  # Normalized around 70
    
    # Weather factor: too hot/cold/dry reduces yield
    temp_factor = 1 - np.abs(merged["temperature_c_weather"] - 25) / 50
    rain_factor = np.clip(merged["rainfall_mm"] / merged["water_requirement_mm"], 0.3, 1.5)
    merged["weather_factor"] = np.clip(temp_factor * 0.6 + rain_factor * 0.4, 0.3, 1.3)
    
    merged["actual_yield"] = (
        merged["expected_yield_tons_per_ha"] *
        merged["health_factor"] *
        merged["weather_factor"] *
        np.random.uniform(0.85, 1.15, len(merged))
    )
    merged["actual_yield"] = np.clip(merged["actual_yield"], 0.1, None).round(2)
    
    return merged


def train(save_model=True):
    """Train the yield prediction model."""
    print(f"\n📈 Training {MODEL_NAME}")
    
    df = create_yield_dataset()
    
    feature_cols = [
        "health_score", "nitrogen_mg_kg", "phosphorus_mg_kg", "potassium_mg_kg",
        "ph", "moisture_pct", "organic_matter_pct",
        "temperature_c_weather", "humidity_pct", "rainfall_mm",
        "solar_radiation_wm2", "expected_yield_tons_per_ha", "water_requirement_mm",
    ]
    
    df = df.dropna(subset=feature_cols + ["actual_yield"])
    
    print(f"   Records: {len(df):,}")
    print(f"   Avg yield: {df['actual_yield'].mean():.2f} tons/ha")
    print(f"   Yield range: {df['actual_yield'].min():.2f} — {df['actual_yield'].max():.2f}")
    
    X = df[feature_cols].values
    y = df["actual_yield"].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    model = GradientBoostingRegressor(
        n_estimators=300, max_depth=7, learning_rate=0.08,
        subsample=0.8, min_samples_leaf=10, random_state=42
    )
    
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="r2")
    print(f"\n   Cross-Val R² scores: {cv_scores.round(4)}")
    print(f"   Mean CV R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    metrics = evaluate_regressor(y_test, y_pred, MODEL_NAME)
    metrics["cv_r2_mean"] = round(cv_scores.mean(), 4)
    
    importance = dict(zip(feature_cols, model.feature_importances_.round(4)))
    metrics["feature_importance"] = dict(sorted(importance.items(), key=lambda x: -x[1]))
    
    reports_dir = os.path.join(PROJECT_ROOT, "results", "reports")
    save_metrics(metrics, reports_dir)
    
    if save_model:
        model_path = os.path.join(PROJECT_ROOT, "models", "crop_intelligence", "yield_predictor.joblib")
        joblib.dump({"model": model, "scaler": scaler, "features": feature_cols}, model_path)
        print(f"  💾 Model saved to {model_path}")
    
    # Dashboard data
    predictions = generate_dashboard_data(df, model, scaler, feature_cols)
    pred_dir = os.path.join(PROJECT_ROOT, "results", "predictions")
    save_predictions(predictions, pred_dir, MODEL_NAME)
    
    return model, scaler, metrics


def generate_dashboard_data(df, model, scaler, feature_cols):
    """Generate yield predictions for the dashboard."""
    X_all = scaler.transform(df[feature_cols].values)
    df["predicted_yield"] = model.predict(X_all)
    
    # Zone-level yield forecasts
    zone_yields = {}
    for zone in df["zone_id"].unique():
        zone_df = df[df["zone_id"] == zone]
        zone_yields[zone] = {
            "crop": zone_df["crop"].iloc[0],
            "avg_predicted_yield": round(zone_df["predicted_yield"].mean(), 2),
            "avg_actual_yield": round(zone_df["actual_yield"].mean(), 2),
            "expected_baseline": round(zone_df["expected_yield_tons_per_ha"].mean(), 2),
            "health_score": round(zone_df["health_score"].mean(), 1),
            "yield_efficiency": round(
                zone_df["predicted_yield"].mean() / zone_df["expected_yield_tons_per_ha"].mean() * 100, 1
            ),
        }
    
    # Risk assessment
    risk_zones = []
    for zone, data in zone_yields.items():
        if data["yield_efficiency"] < 70:
            risk_zones.append({
                "zone": zone,
                "efficiency": data["yield_efficiency"],
                "action": "Investigate soil health and irrigation — yield significantly below potential",
            })
    
    return {
        "zone_yields": zone_yields,
        "risk_zones": risk_zones,
        "overall_avg_yield": round(df["predicted_yield"].mean(), 2),
        "yield_distribution": {
            "min": round(df["predicted_yield"].min(), 2),
            "q1": round(df["predicted_yield"].quantile(0.25), 2),
            "median": round(df["predicted_yield"].median(), 2),
            "q3": round(df["predicted_yield"].quantile(0.75), 2),
            "max": round(df["predicted_yield"].max(), 2),
        },
    }


if __name__ == "__main__":
    train()
