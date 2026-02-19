"""
AgriSense AI — Smart Irrigation Optimizer
===========================================
Predicts optimal irrigation schedules using soil moisture, weather data,
crop water needs, and evapotranspiration estimates.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.utils.preprocessing import (
    load_and_clean_soil_data, load_and_clean_weather_data,
    load_crop_database, estimate_eto
)
from models.utils.evaluation import evaluate_regressor, save_metrics, save_predictions

MODEL_NAME = "Irrigation Optimizer"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def create_irrigation_dataset(soil_path=None, weather_path=None, crop_path=None):
    """
    Merge soil, weather, and crop data to create an irrigation optimization dataset.
    
    Target: irrigation_need_mm — how much water is needed (0 = no irrigation needed).
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
    
    # Assign random crops to zones for simulation
    np.random.seed(42)
    zone_crops = {}
    common_crops = crop_db.sample(8, random_state=42)["crop_name"].values
    for i, zone in enumerate(soil_df["zone_id"].unique()):
        zone_crops[zone] = common_crops[i % len(common_crops)]
    
    soil_df["crop"] = soil_df["zone_id"].map(zone_crops)
    
    # Merge crop water requirements
    soil_df = soil_df.merge(
        crop_db[["crop_name", "water_requirement_mm"]],
        left_on="crop", right_on="crop_name", how="left"
    ).drop("crop_name", axis=1)
    
    # Get nearest weather reading for each soil reading
    soil_df["date"] = soil_df["timestamp"].dt.date
    weather_df["date"] = weather_df["timestamp"].dt.date
    
    # Daily weather aggregation
    daily_weather = weather_df.groupby("date").agg({
        "temperature_c": "mean",
        "humidity_pct": "mean",
        "rainfall_mm": "sum",
        "solar_radiation_wm2": "mean",
        "wind_speed_kmh": "mean",
        "evapotranspiration_est": "mean",
    }).reset_index()
    
    merged = soil_df.merge(daily_weather, on="date", how="left", suffixes=("_soil", "_weather"))
    merged = merged.dropna(subset=["temperature_c_weather"])
    
    # Calculate irrigation need
    # Field capacity varies by soil type
    field_capacity = {
        "Loamy": 40, "Clay": 50, "Sandy": 20, "Silt": 45,
        "Clay Loam": 48, "Sandy Loam": 28, "Peaty": 60
    }
    merged["field_capacity"] = merged["soil_type"].map(field_capacity).fillna(35)
    
    # Irrigation need = max(0, (field_capacity * 0.5 - current_moisture) + ETo - rainfall)
    merged["moisture_deficit"] = merged["field_capacity"] * 0.5 - merged["moisture_pct"]
    merged["irrigation_need_mm"] = np.clip(
        merged["moisture_deficit"] + merged["evapotranspiration_est"] * 5 - merged["rainfall_mm"] * 0.8,
        0, 50
    )
    
    return merged


def train(save_model=True):
    """Train the irrigation optimization model."""
    print(f"\n💦 Training {MODEL_NAME}")
    
    df = create_irrigation_dataset()
    
    feature_cols = [
        "moisture_pct", "soil_temperature_c", "ec_mscm",
        "temperature_c_weather", "humidity_pct", "rainfall_mm",
        "solar_radiation_wm2", "wind_speed_kmh", "evapotranspiration_est",
        "water_requirement_mm", "field_capacity",
    ]
    
    df = df.dropna(subset=feature_cols + ["irrigation_need_mm"])
    
    print(f"   Records: {len(df):,}")
    print(f"   Avg irrigation need: {df['irrigation_need_mm'].mean():.1f} mm")
    
    X = df[feature_cols].values
    y = df["irrigation_need_mm"].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = GradientBoostingRegressor(
        n_estimators=250, max_depth=7, learning_rate=0.1,
        subsample=0.8, random_state=42
    )
    
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="r2")
    print(f"\n   Cross-Val R² scores: {cv_scores.round(4)}")
    print(f"   Mean CV R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    metrics = evaluate_regressor(y_test, y_pred, MODEL_NAME)
    metrics["cv_r2_mean"] = round(cv_scores.mean(), 4)
    
    # Feature importance
    importance = dict(zip(feature_cols, model.feature_importances_.round(4)))
    metrics["feature_importance"] = dict(sorted(importance.items(), key=lambda x: -x[1]))
    
    reports_dir = os.path.join(PROJECT_ROOT, "results", "reports")
    save_metrics(metrics, reports_dir)
    
    if save_model:
        model_path = os.path.join(PROJECT_ROOT, "models", "water_management", "irrigation_optimizer.joblib")
        joblib.dump({"model": model, "features": feature_cols}, model_path)
        print(f"  💾 Model saved to {model_path}")
    
    # Dashboard data
    predictions = generate_dashboard_data(df, model, feature_cols)
    pred_dir = os.path.join(PROJECT_ROOT, "results", "predictions")
    save_predictions(predictions, pred_dir, MODEL_NAME)
    
    return model, metrics


def generate_dashboard_data(df, model, feature_cols):
    """Generate irrigation schedule and analytics for the dashboard."""
    X_all = df[feature_cols].values
    df["predicted_need_mm"] = model.predict(X_all)
    
    # Zone-level irrigation schedule
    zone_schedule = {}
    for zone in df["zone_id"].unique():
        zone_df = df[df["zone_id"] == zone].sort_values("timestamp")
        recent = zone_df.tail(30)
        
        needs_irrigation = recent["predicted_need_mm"].mean() > 5
        
        zone_schedule[zone] = {
            "crop": zone_df["crop"].iloc[0],
            "soil_type": zone_df["soil_type"].iloc[0],
            "avg_moisture": round(recent["moisture_pct"].mean(), 1),
            "avg_need_mm": round(recent["predicted_need_mm"].mean(), 1),
            "max_need_mm": round(recent["predicted_need_mm"].max(), 1),
            "needs_irrigation": bool(needs_irrigation),
            "priority": "High" if recent["predicted_need_mm"].mean() > 15 else ("Medium" if needs_irrigation else "Low"),
            "recommended_frequency": "Daily" if recent["predicted_need_mm"].mean() > 15 else ("Every 2 days" if needs_irrigation else "Every 3-4 days"),
        }
    
    # Water savings estimate
    total_predicted = df["predicted_need_mm"].sum()
    naive_irrigation = len(df) * 20  # Assume 20mm uniform irrigation
    savings_pct = round((1 - total_predicted / naive_irrigation) * 100, 1)
    
    return {
        "zone_schedule": zone_schedule,
        "water_savings_pct": max(0, savings_pct),
        "total_water_needed_mm": round(total_predicted, 0),
        "avg_daily_need": round(df.groupby("date")["predicted_need_mm"].mean().mean(), 1),
        "drought_risk_zones": [z for z, s in zone_schedule.items() if s["priority"] == "High"],
        "weekly_forecast": df.groupby(df["timestamp"].dt.isocalendar().week)["predicted_need_mm"].mean().round(1).to_dict(),
    }


if __name__ == "__main__":
    train()
