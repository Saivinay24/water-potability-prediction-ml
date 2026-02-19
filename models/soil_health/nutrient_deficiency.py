"""
AgriSense AI — Nutrient Deficiency Detector
=============================================
Multi-label classifier that identifies N/P/K deficiencies and pH imbalance,
then recommends specific amendments with dosages.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.multioutput import MultiOutputClassifier

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.utils.preprocessing import load_and_clean_soil_data, load_crop_database
from models.utils.evaluation import evaluate_classifier, save_metrics, save_predictions

MODEL_NAME = "Nutrient Deficiency Detector"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

FEATURE_COLS = [
    "nitrogen_mg_kg", "phosphorus_mg_kg", "potassium_mg_kg",
    "ph", "organic_matter_pct", "moisture_pct", "ec_mscm"
]

# Default thresholds (general agriculture)
DEFICIENCY_THRESHOLDS = {
    "nitrogen": {"low": 40, "moderate": 60, "adequate": 80},
    "phosphorus": {"low": 15, "moderate": 25, "adequate": 40},
    "potassium": {"low": 25, "moderate": 35, "adequate": 50},
    "ph_low": 5.5,
    "ph_high": 8.0,
}

AMENDMENT_RECOMMENDATIONS = {
    "N_deficient": [
        {"amendment": "Urea (46-0-0)", "dosage": "60-100 kg/ha", "timing": "Split application: 50% at sowing, 50% at 30 days"},
        {"amendment": "Ammonium Sulfate (21-0-0-24S)", "dosage": "120-180 kg/ha", "timing": "Pre-sowing or side-dress"},
        {"amendment": "Neem-coated Urea", "dosage": "60-100 kg/ha", "timing": "Slow release, apply at sowing"},
    ],
    "P_deficient": [
        {"amendment": "DAP (18-46-0)", "dosage": "50-80 kg/ha", "timing": "Apply at sowing as basal dose"},
        {"amendment": "SSP (0-16-0)", "dosage": "150-250 kg/ha", "timing": "Basal application"},
        {"amendment": "Rock Phosphate", "dosage": "200-400 kg/ha", "timing": "Pre-sowing, works best in acidic soils"},
    ],
    "K_deficient": [
        {"amendment": "MOP - Muriate of Potash (0-0-60)", "dosage": "40-80 kg/ha", "timing": "Basal or split application"},
        {"amendment": "SOP - Sulfate of Potash (0-0-50)", "dosage": "50-100 kg/ha", "timing": "For chloride-sensitive crops"},
        {"amendment": "Wood Ash", "dosage": "500-1000 kg/ha", "timing": "Pre-sowing, also raises pH"},
    ],
    "pH_low": [
        {"amendment": "Agricultural Lime (CaCO₃)", "dosage": "2-4 tons/ha", "timing": "Apply 2-3 months before sowing"},
        {"amendment": "Dolomite Lime", "dosage": "1.5-3 tons/ha", "timing": "Also supplies Mg, apply before plowing"},
    ],
    "pH_high": [
        {"amendment": "Gypsum (CaSO₄)", "dosage": "2-5 tons/ha", "timing": "Apply before plowing season"},
        {"amendment": "Sulfur (Eleite)", "dosage": "200-500 kg/ha", "timing": "Apply and incorporate into soil"},
        {"amendment": "Organic Matter / Compost", "dosage": "10-20 tons/ha", "timing": "Regular annual application"},
    ],
}


def create_deficiency_labels(df, crop_db=None):
    """Create multi-label deficiency targets from soil data."""
    thresholds = DEFICIENCY_THRESHOLDS
    
    df["N_deficient"] = (df["nitrogen_mg_kg"] < thresholds["nitrogen"]["moderate"]).astype(int)
    df["P_deficient"] = (df["phosphorus_mg_kg"] < thresholds["phosphorus"]["moderate"]).astype(int)
    df["K_deficient"] = (df["potassium_mg_kg"] < thresholds["potassium"]["moderate"]).astype(int)
    df["pH_imbalanced"] = ((df["ph"] < thresholds["ph_low"]) | (df["ph"] > thresholds["ph_high"])).astype(int)
    
    # Severity levels
    df["N_severity"] = pd.cut(
        df["nitrogen_mg_kg"],
        bins=[0, thresholds["nitrogen"]["low"], thresholds["nitrogen"]["moderate"], thresholds["nitrogen"]["adequate"], 999],
        labels=["Critical", "Low", "Moderate", "Adequate"]
    )
    df["P_severity"] = pd.cut(
        df["phosphorus_mg_kg"],
        bins=[0, thresholds["phosphorus"]["low"], thresholds["phosphorus"]["moderate"], thresholds["phosphorus"]["adequate"], 999],
        labels=["Critical", "Low", "Moderate", "Adequate"]
    )
    df["K_severity"] = pd.cut(
        df["potassium_mg_kg"],
        bins=[0, thresholds["potassium"]["low"], thresholds["potassium"]["moderate"], thresholds["potassium"]["adequate"], 999],
        labels=["Critical", "Low", "Moderate", "Adequate"]
    )
    
    return df


def train(data_path=None, save_model=True):
    """Train the multi-label nutrient deficiency classifier."""
    if data_path is None:
        data_path = os.path.join(PROJECT_ROOT, "data", "raw", "soil_sensors.csv")
    
    print(f"\n🧪 Training {MODEL_NAME}")
    print(f"   Data source: {data_path}")
    
    df = load_and_clean_soil_data(data_path)
    df = create_deficiency_labels(df)
    
    target_cols = ["N_deficient", "P_deficient", "K_deficient", "pH_imbalanced"]
    
    print(f"   Records: {len(df):,}")
    print(f"   Deficiency rates:")
    for col in target_cols:
        rate = df[col].mean() * 100
        print(f"     {col}: {rate:.1f}%")
    
    X = df[FEATURE_COLS].values
    Y = df[target_cols].values
    
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    
    # Multi-output Random Forest
    base_rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1)
    model = MultiOutputClassifier(base_rf)
    model.fit(X_train, Y_train)
    
    Y_pred = model.predict(X_test)
    
    # Evaluate each label
    all_metrics = {"model_name": MODEL_NAME, "labels": {}}
    for i, col in enumerate(target_cols):
        metrics = evaluate_classifier(Y_test[:, i], Y_pred[:, i], f"{MODEL_NAME} — {col}")
        all_metrics["labels"][col] = metrics
    
    # Save
    reports_dir = os.path.join(PROJECT_ROOT, "results", "reports")
    save_metrics(all_metrics, reports_dir)
    
    if save_model:
        model_path = os.path.join(PROJECT_ROOT, "models", "soil_health", "nutrient_deficiency.joblib")
        joblib.dump({"model": model, "features": FEATURE_COLS, "targets": target_cols}, model_path)
        print(f"  💾 Model saved to {model_path}")
    
    # Dashboard data
    predictions = generate_dashboard_data(df, model, target_cols)
    pred_dir = os.path.join(PROJECT_ROOT, "results", "predictions")
    save_predictions(predictions, pred_dir, MODEL_NAME)
    
    return model, all_metrics


def generate_dashboard_data(df, model, target_cols):
    """Generate deficiency analysis summaries for the dashboard."""
    X_all = df[FEATURE_COLS].values
    preds = model.predict(X_all)
    
    for i, col in enumerate(target_cols):
        df[f"pred_{col}"] = preds[:, i]
    
    # Zone-level deficiency summary
    zone_summary = {}
    for zone in df["zone_id"].unique():
        zone_df = df[df["zone_id"] == zone]
        zone_summary[zone] = {
            "n_deficiency_rate": round(zone_df["pred_N_deficient"].mean() * 100, 1),
            "p_deficiency_rate": round(zone_df["pred_P_deficient"].mean() * 100, 1),
            "k_deficiency_rate": round(zone_df["pred_K_deficient"].mean() * 100, 1),
            "ph_imbalance_rate": round(zone_df["pred_pH_imbalanced"].mean() * 100, 1),
            "avg_n": round(zone_df["nitrogen_mg_kg"].mean(), 1),
            "avg_p": round(zone_df["phosphorus_mg_kg"].mean(), 1),
            "avg_k": round(zone_df["potassium_mg_kg"].mean(), 1),
            "avg_ph": round(zone_df["ph"].mean(), 2),
        }
    
    return {
        "overall_deficiency_rates": {
            col: round(df[f"pred_{col}"].mean() * 100, 1) for col in target_cols
        },
        "zone_analysis": zone_summary,
        "amendment_guide": AMENDMENT_RECOMMENDATIONS,
        "thresholds": DEFICIENCY_THRESHOLDS,
    }


def diagnose(sensor_reading):
    """
    Diagnose nutrient deficiencies for a single reading.
    
    Returns deficiency flags, severity, and specific amendment recommendations.
    """
    result = {"deficiencies": [], "recommendations": [], "severity": "none"}
    
    n = sensor_reading.get("nitrogen_mg_kg", 0)
    p = sensor_reading.get("phosphorus_mg_kg", 0)
    k = sensor_reading.get("potassium_mg_kg", 0)
    ph = sensor_reading.get("ph", 7.0)
    
    if n < DEFICIENCY_THRESHOLDS["nitrogen"]["moderate"]:
        severity = "Critical" if n < DEFICIENCY_THRESHOLDS["nitrogen"]["low"] else "Low"
        result["deficiencies"].append({"nutrient": "Nitrogen", "value": n, "severity": severity})
        result["recommendations"].extend(AMENDMENT_RECOMMENDATIONS["N_deficient"])
    
    if p < DEFICIENCY_THRESHOLDS["phosphorus"]["moderate"]:
        severity = "Critical" if p < DEFICIENCY_THRESHOLDS["phosphorus"]["low"] else "Low"
        result["deficiencies"].append({"nutrient": "Phosphorus", "value": p, "severity": severity})
        result["recommendations"].extend(AMENDMENT_RECOMMENDATIONS["P_deficient"])
    
    if k < DEFICIENCY_THRESHOLDS["potassium"]["moderate"]:
        severity = "Critical" if k < DEFICIENCY_THRESHOLDS["potassium"]["low"] else "Low"
        result["deficiencies"].append({"nutrient": "Potassium", "value": k, "severity": severity})
        result["recommendations"].extend(AMENDMENT_RECOMMENDATIONS["K_deficient"])
    
    if ph < DEFICIENCY_THRESHOLDS["ph_low"]:
        result["deficiencies"].append({"nutrient": "pH (Acidic)", "value": ph, "severity": "Imbalanced"})
        result["recommendations"].extend(AMENDMENT_RECOMMENDATIONS["pH_low"])
    elif ph > DEFICIENCY_THRESHOLDS["ph_high"]:
        result["deficiencies"].append({"nutrient": "pH (Alkaline)", "value": ph, "severity": "Imbalanced"})
        result["recommendations"].extend(AMENDMENT_RECOMMENDATIONS["pH_high"])
    
    if result["deficiencies"]:
        severities = [d["severity"] for d in result["deficiencies"]]
        if "Critical" in severities:
            result["severity"] = "critical"
        else:
            result["severity"] = "moderate"
    
    return result


if __name__ == "__main__":
    train()
