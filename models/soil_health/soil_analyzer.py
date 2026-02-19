"""
AgriSense AI — Soil Health Analyzer
=====================================
Ensemble ML model that scores soil health (0-100) and categorizes it
based on NPK levels, pH, organic matter, moisture, and EC readings.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.model_selection import train_test_split, cross_val_score

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.utils.preprocessing import (
    load_and_clean_soil_data, generate_soil_health_score,
    categorize_health_score, prepare_features
)
from models.utils.evaluation import evaluate_regressor, save_metrics, save_predictions, get_feature_importance

# ─── Configuration ────────────────────────────────────────────────────────────

FEATURE_COLS = [
    "nitrogen_mg_kg", "phosphorus_mg_kg", "potassium_mg_kg",
    "ph", "organic_matter_pct", "moisture_pct",
    "soil_temperature_c", "ec_mscm", "npk_ratio", "nutrient_total"
]

MODEL_NAME = "Soil Health Analyzer"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


# ─── Model Training ──────────────────────────────────────────────────────────

def train(data_path=None, save_model=True):
    """
    Train the soil health analysis ensemble model.
    
    Pipeline:
    1. Load & clean soil sensor data
    2. Generate soil health scores as target
    3. Train Random Forest + GBR ensemble
    4. Evaluate with cross-validation
    5. Save model and metrics
    """
    if data_path is None:
        data_path = os.path.join(PROJECT_ROOT, "data", "raw", "soil_sensors.csv")
    
    print(f"\n🌱 Training {MODEL_NAME}")
    print(f"   Data source: {data_path}")
    
    # Load and preprocess
    df = load_and_clean_soil_data(data_path)
    
    # Generate target: soil health score
    df["health_score"] = df.apply(generate_soil_health_score, axis=1)
    df["health_category"] = df["health_score"].apply(categorize_health_score)
    
    print(f"   Records: {len(df):,}")
    print(f"   Health Distribution:")
    print(f"   {df['health_category'].value_counts().to_dict()}")
    
    # Prepare features
    X, y, scaler = prepare_features(df, FEATURE_COLS, "health_score", scale=True)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Build ensemble
    rf = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    gbr = GradientBoostingRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
    
    ensemble = VotingRegressor([("rf", rf), ("gbr", gbr)])
    
    # Cross-validation
    cv_scores = cross_val_score(ensemble, X_train, y_train, cv=5, scoring="r2")
    print(f"\n   Cross-Val R² scores: {cv_scores.round(4)}")
    print(f"   Mean CV R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    # Final training
    ensemble.fit(X_train, y_train)
    y_pred = ensemble.predict(X_test)
    
    # Evaluate
    metrics = evaluate_regressor(y_test, y_pred, MODEL_NAME)
    metrics["cv_r2_mean"] = round(cv_scores.mean(), 4)
    metrics["cv_r2_std"] = round(cv_scores.std(), 4)
    
    # Feature importance (from RF component)
    rf_model = ensemble.named_estimators_["rf"]
    metrics["feature_importance"] = get_feature_importance(rf_model, FEATURE_COLS)
    
    # Save
    reports_dir = os.path.join(PROJECT_ROOT, "results", "reports")
    save_metrics(metrics, reports_dir)
    
    if save_model:
        model_path = os.path.join(PROJECT_ROOT, "models", "soil_health", "soil_analyzer.joblib")
        joblib.dump({"model": ensemble, "scaler": scaler, "features": FEATURE_COLS}, model_path)
        print(f"  💾 Model saved to {model_path}")
    
    # Generate predictions for dashboard
    predictions = generate_dashboard_data(df, ensemble, scaler)
    pred_dir = os.path.join(PROJECT_ROOT, "results", "predictions")
    save_predictions(predictions, pred_dir, MODEL_NAME)
    
    return ensemble, scaler, metrics


def generate_dashboard_data(df, model, scaler):
    """Generate zone-level soil health summaries for the dashboard."""
    X_all, _ = prepare_features(df, FEATURE_COLS, scale=False)
    X_scaled = scaler.transform(X_all)
    df["predicted_score"] = model.predict(X_scaled)
    df["predicted_category"] = df["predicted_score"].apply(categorize_health_score)
    
    # Zone-level aggregation
    zone_summary = df.groupby("zone_id").agg({
        "predicted_score": "mean",
        "nitrogen_mg_kg": "mean",
        "phosphorus_mg_kg": "mean",
        "potassium_mg_kg": "mean",
        "ph": "mean",
        "organic_matter_pct": "mean",
        "moisture_pct": "mean",
    }).round(2)
    
    zone_summary["category"] = zone_summary["predicted_score"].apply(categorize_health_score)
    
    # Overall stats
    overall = {
        "avg_score": round(df["predicted_score"].mean(), 1),
        "min_score": round(df["predicted_score"].min(), 1),
        "max_score": round(df["predicted_score"].max(), 1),
        "category_distribution": df["predicted_category"].value_counts().to_dict(),
        "zones": zone_summary.reset_index().to_dict(orient="records"),
        "recent_readings": df.tail(20)[FEATURE_COLS + ["zone_id", "predicted_score", "predicted_category"]].to_dict(orient="records"),
    }
    
    return overall


# ─── Prediction Interface ────────────────────────────────────────────────────

def predict(sensor_reading, model_path=None):
    """
    Predict soil health for a single sensor reading.
    
    Args:
        sensor_reading: dict with keys matching FEATURE_COLS
        model_path: path to saved model (optional)
    
    Returns:
        dict with score, category, and recommendations
    """
    if model_path is None:
        model_path = os.path.join(PROJECT_ROOT, "models", "soil_health", "soil_analyzer.joblib")
    
    saved = joblib.load(model_path)
    model, scaler, features = saved["model"], saved["scaler"], saved["features"]
    
    X = np.array([[sensor_reading.get(f, 0) for f in features]])
    X_scaled = scaler.transform(X)
    score = model.predict(X_scaled)[0]
    category = categorize_health_score(score)
    
    # Generate recommendations
    recommendations = []
    if sensor_reading.get("nitrogen_mg_kg", 0) < 40:
        recommendations.append("⚠️ Low Nitrogen: Apply nitrogen-rich fertilizer (Urea) at 50-80 kg/ha")
    if sensor_reading.get("phosphorus_mg_kg", 0) < 20:
        recommendations.append("⚠️ Low Phosphorus: Apply DAP or SSP at 40-60 kg/ha")
    if sensor_reading.get("potassium_mg_kg", 0) < 30:
        recommendations.append("⚠️ Low Potassium: Apply MOP (Muriate of Potash) at 30-50 kg/ha")
    if sensor_reading.get("ph", 7) < 5.5:
        recommendations.append("⚠️ Acidic Soil: Apply agricultural lime at 2-4 tons/ha")
    elif sensor_reading.get("ph", 7) > 8.0:
        recommendations.append("⚠️ Alkaline Soil: Apply gypsum at 2-3 tons/ha")
    if sensor_reading.get("organic_matter_pct", 3) < 2.0:
        recommendations.append("⚠️ Low Organic Matter: Add compost/FYM at 10-15 tons/ha")
    
    if not recommendations:
        recommendations.append("✅ Soil health is good. Maintain current practices.")
    
    return {
        "score": round(score, 1),
        "category": category,
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    train()
