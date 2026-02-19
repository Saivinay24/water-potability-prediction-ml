"""
AgriSense AI — Crop Recommendation Engine
============================================
Recommends optimal crops based on soil conditions, climate data,
and growing season using ensemble classification.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.utils.preprocessing import load_and_clean_soil_data, load_crop_database, get_season
from models.utils.evaluation import evaluate_classifier, save_metrics, save_predictions

MODEL_NAME = "Crop Recommender"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def create_crop_recommendation_dataset(soil_path=None, crop_path=None):
    """
    Create a labeled training dataset by matching soil profiles to suitable crops.
    For each soil reading, find the best matching crop from the crop database.
    """
    if soil_path is None:
        soil_path = os.path.join(PROJECT_ROOT, "data", "raw", "soil_sensors.csv")
    if crop_path is None:
        crop_path = os.path.join(PROJECT_ROOT, "data", "raw", "crop_database.csv")
    
    soil_df = load_and_clean_soil_data(soil_path)
    crop_db = load_crop_database(crop_path)
    
    records = []
    for _, soil_row in soil_df.iterrows():
        n = soil_row["nitrogen_mg_kg"]
        p = soil_row["phosphorus_mg_kg"]
        k = soil_row["potassium_mg_kg"]
        ph = soil_row["ph"]
        moisture = soil_row["moisture_pct"]
        temp = soil_row["soil_temperature_c"]
        season = soil_row.get("season", "Kharif")
        
        # Score each crop's suitability
        best_crops = []
        for _, crop_row in crop_db.iterrows():
            score = 0
            # N fitness
            if crop_row["nitrogen_min_mg_kg"] <= n <= crop_row["nitrogen_max_mg_kg"]:
                score += 25
            elif abs(n - (crop_row["nitrogen_min_mg_kg"] + crop_row["nitrogen_max_mg_kg"]) / 2) < 30:
                score += 10
            # P fitness
            if crop_row["phosphorus_min_mg_kg"] <= p <= crop_row["phosphorus_max_mg_kg"]:
                score += 20
            elif abs(p - (crop_row["phosphorus_min_mg_kg"] + crop_row["phosphorus_max_mg_kg"]) / 2) < 20:
                score += 8
            # K fitness
            if crop_row["potassium_min_mg_kg"] <= k <= crop_row["potassium_max_mg_kg"]:
                score += 20
            elif abs(k - (crop_row["potassium_min_mg_kg"] + crop_row["potassium_max_mg_kg"]) / 2) < 25:
                score += 8
            # pH fitness
            if crop_row["ph_min"] <= ph <= crop_row["ph_max"]:
                score += 20
            elif abs(ph - (crop_row["ph_min"] + crop_row["ph_max"]) / 2) < 1:
                score += 8
            # Temperature fitness
            if crop_row["temperature_min_c"] <= temp <= crop_row["temperature_max_c"]:
                score += 15
            
            # Season bonus
            crop_season = crop_row["growing_season"]
            if crop_season == "Annual" or crop_season == "Year-round" or crop_season == season:
                score += 10
            
            best_crops.append((crop_row["crop_name"], score))
        
        # Pick top crop
        best_crops.sort(key=lambda x: -x[1])
        best_crop = best_crops[0][0]
        
        records.append({
            "nitrogen_mg_kg": n,
            "phosphorus_mg_kg": p,
            "potassium_mg_kg": k,
            "ph": ph,
            "organic_matter_pct": soil_row["organic_matter_pct"],
            "moisture_pct": moisture,
            "soil_temperature_c": temp,
            "ec_mscm": soil_row["ec_mscm"],
            "season_encoded": {"Kharif": 0, "Rabi": 1, "Zaid": 2}.get(season, 0),
            "recommended_crop": best_crop,
        })
    
    return pd.DataFrame(records)


def train(save_model=True):
    """Train the crop recommendation ensemble classifier."""
    print(f"\n🌾 Training {MODEL_NAME}")
    
    df = create_crop_recommendation_dataset()
    
    feature_cols = [
        "nitrogen_mg_kg", "phosphorus_mg_kg", "potassium_mg_kg",
        "ph", "organic_matter_pct", "moisture_pct",
        "soil_temperature_c", "ec_mscm", "season_encoded"
    ]
    
    le = LabelEncoder()
    df["crop_encoded"] = le.fit_transform(df["recommended_crop"])
    
    print(f"   Records: {len(df):,}")
    print(f"   Unique crops: {df['recommended_crop'].nunique()}")
    print(f"   Top crops: {df['recommended_crop'].value_counts().head(5).to_dict()}")
    
    X = df[feature_cols].values
    y = df["crop_encoded"].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Ensemble: RF + KNN + GBR
    rf = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    knn = KNeighborsClassifier(n_neighbors=7, weights="distance")
    gbr = GradientBoostingClassifier(n_estimators=150, max_depth=6, learning_rate=0.1, random_state=42)
    
    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("knn", knn), ("gbr", gbr)],
        voting="soft"
    )
    
    cv_scores = cross_val_score(ensemble, X_train, y_train, cv=5, scoring="accuracy")
    print(f"\n   Cross-Val Accuracy: {cv_scores.round(4)}")
    print(f"   Mean CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    ensemble.fit(X_train, y_train)
    y_pred = ensemble.predict(X_test)
    
    metrics = evaluate_classifier(
        le.inverse_transform(y_test),
        le.inverse_transform(y_pred),
        MODEL_NAME
    )
    metrics["cv_accuracy_mean"] = round(cv_scores.mean(), 4)
    
    reports_dir = os.path.join(PROJECT_ROOT, "results", "reports")
    save_metrics(metrics, reports_dir)
    
    if save_model:
        model_path = os.path.join(PROJECT_ROOT, "models", "crop_intelligence", "crop_recommender.joblib")
        joblib.dump({
            "model": ensemble, "scaler": scaler,
            "label_encoder": le, "features": feature_cols
        }, model_path)
        print(f"  💾 Model saved to {model_path}")
    
    # Dashboard data
    predictions = generate_dashboard_data(df, ensemble, scaler, le, feature_cols)
    pred_dir = os.path.join(PROJECT_ROOT, "results", "predictions")
    save_predictions(predictions, pred_dir, MODEL_NAME)
    
    return ensemble, scaler, le, metrics


def generate_dashboard_data(df, model, scaler, le, feature_cols):
    """Generate crop recommendation summaries for the dashboard."""
    crop_db = load_crop_database()
    
    # Zone-level recommendations
    zone_recommendations = {}
    for zone in df.get("zone_id", pd.Series(dtype=str)).unique() if "zone_id" in df.columns else []:
        zone_df = df[df["zone_id"] == zone]
        X_zone = scaler.transform(zone_df[feature_cols].values)
        probas = model.predict_proba(X_zone).mean(axis=0)
        top_indices = probas.argsort()[-5:][::-1]
        
        top_crops = []
        for idx in top_indices:
            crop_name = le.inverse_transform([idx])[0]
            crop_info = crop_db[crop_db["crop_name"] == crop_name]
            top_crops.append({
                "crop": crop_name,
                "confidence": round(float(probas[idx]) * 100, 1),
                "expected_yield": float(crop_info["expected_yield_tons_per_ha"].values[0]) if len(crop_info) > 0 else 0,
            })
        zone_recommendations[zone] = top_crops
    
    return {
        "overall_distribution": df["recommended_crop"].value_counts().head(10).to_dict(),
        "zone_recommendations": zone_recommendations,
        "crop_database_size": len(crop_db),
        "seasons_covered": ["Kharif", "Rabi", "Zaid", "Annual"],
    }


def recommend(soil_reading, top_n=5):
    """
    Recommend top-N crops for given soil conditions.
    
    Args:
        soil_reading: dict with soil sensor values
        top_n: number of recommendations to return
    
    Returns:
        list of crop recommendations with confidence and expected yield
    """
    model_path = os.path.join(PROJECT_ROOT, "models", "crop_intelligence", "crop_recommender.joblib")
    saved = joblib.load(model_path)
    model, scaler, le = saved["model"], saved["scaler"], saved["label_encoder"]
    feature_cols = saved["features"]
    
    X = np.array([[soil_reading.get(f, 0) for f in feature_cols]])
    X_scaled = scaler.transform(X)
    
    probas = model.predict_proba(X_scaled)[0]
    top_indices = probas.argsort()[-top_n:][::-1]
    
    crop_db = load_crop_database()
    
    recommendations = []
    for idx in top_indices:
        crop_name = le.inverse_transform([idx])[0]
        crop_info = crop_db[crop_db["crop_name"] == crop_name]
        
        rec = {
            "crop": crop_name,
            "confidence": round(float(probas[idx]) * 100, 1),
        }
        if len(crop_info) > 0:
            rec.update({
                "expected_yield_tons_ha": float(crop_info["expected_yield_tons_per_ha"].values[0]),
                "water_requirement_mm": int(crop_info["water_requirement_mm"].values[0]),
                "growing_season": crop_info["growing_season"].values[0],
            })
        recommendations.append(rec)
    
    return recommendations


if __name__ == "__main__":
    train()
