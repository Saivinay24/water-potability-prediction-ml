"""
AgriSense AI — Water Quality Classifier
=========================================
XGBoost-based water quality grading (A-F) with SMOTE class balancing,
irrigation suitability assessment, and treatment recommendations.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.utils.preprocessing import load_and_clean_water_data, prepare_features, encode_categorical
from models.utils.evaluation import evaluate_classifier, save_metrics, save_predictions, get_feature_importance

MODEL_NAME = "Water Quality Classifier"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

FEATURE_COLS = [
    "ph", "tds_ppm", "turbidity_ntu", "dissolved_oxygen_mg_l",
    "hardness_mg_l", "chloride_mg_l", "sulfate_mg_l", "nitrate_mg_l",
    "water_temperature_c", "tds_turbidity_ratio", "ion_balance"
]

# WHO/BIS irrigation water quality limits
IRRIGATION_LIMITS = {
    "ph": {"min": 6.0, "max": 8.5, "unit": ""},
    "tds_ppm": {"max": 2000, "unit": "ppm"},
    "chloride_mg_l": {"max": 350, "unit": "mg/L"},
    "sulfate_mg_l": {"max": 400, "unit": "mg/L"},
    "hardness_mg_l": {"max": 500, "unit": "mg/L"},
}

TREATMENT_RECOMMENDATIONS = {
    "A": {"status": "Excellent", "treatment": "No treatment needed. Safe for irrigation and livestock."},
    "B": {"status": "Good", "treatment": "Basic filtration recommended. Suitable for most crops."},
    "C": {"status": "Moderate", "treatment": "Sediment filtration + pH adjustment recommended. Monitor sensitive crops."},
    "D": {"status": "Poor", "treatment": "Multi-stage treatment required: sedimentation → filtration → chemical treatment. Limit to tolerant crops."},
    "F": {"status": "Unsafe", "treatment": "Do NOT use for irrigation. Full treatment required: reverse osmosis or advanced oxidation. Investigate contamination source."},
}


def train(data_path=None, save_model=True):
    """Train the water quality classification model with class balancing."""
    if data_path is None:
        data_path = os.path.join(PROJECT_ROOT, "data", "raw", "water_quality.csv")
    
    print(f"\n💧 Training {MODEL_NAME}")
    print(f"   Data source: {data_path}")
    
    df = load_and_clean_water_data(data_path)
    
    # Encode target
    le = LabelEncoder()
    df["quality_encoded"] = le.fit_transform(df["quality_grade"])
    
    print(f"   Records: {len(df):,}")
    print(f"   Grade distribution:")
    print(f"   {df['quality_grade'].value_counts().to_dict()}")
    
    X = df[FEATURE_COLS].values
    y = df["quality_encoded"].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Handle class imbalance with sample weights
    class_counts = np.bincount(y_train)
    total = len(y_train)
    class_weights = {i: total / (len(class_counts) * count) for i, count in enumerate(class_counts) if count > 0}
    sample_weights = np.array([class_weights[yi] for yi in y_train])
    
    # Gradient Boosting (XGBoost-style)
    model = GradientBoostingClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train, sample_weight=sample_weights)
    
    y_pred = model.predict(X_test)
    
    # Evaluate
    grade_labels = le.classes_
    metrics = evaluate_classifier(
        le.inverse_transform(y_test),
        le.inverse_transform(y_pred),
        MODEL_NAME,
        labels=list(grade_labels)
    )
    metrics["feature_importance"] = get_feature_importance(model, FEATURE_COLS)
    
    # Save
    reports_dir = os.path.join(PROJECT_ROOT, "results", "reports")
    save_metrics(metrics, reports_dir)
    
    if save_model:
        model_path = os.path.join(PROJECT_ROOT, "models", "water_management", "water_quality.joblib")
        joblib.dump({
            "model": model, "label_encoder": le,
            "features": FEATURE_COLS
        }, model_path)
        print(f"  💾 Model saved to {model_path}")
    
    # Dashboard data
    predictions = generate_dashboard_data(df, model, le)
    pred_dir = os.path.join(PROJECT_ROOT, "results", "predictions")
    save_predictions(predictions, pred_dir, MODEL_NAME)
    
    return model, le, metrics


def generate_dashboard_data(df, model, le):
    """Generate water quality summaries for the dashboard."""
    X_all = df[FEATURE_COLS].values
    preds = model.predict(X_all)
    df["predicted_grade"] = le.inverse_transform(preds)
    
    # Source-level analysis
    source_analysis = {}
    for source in df["source_type"].unique():
        source_df = df[df["source_type"] == source]
        source_analysis[source] = {
            "grade_distribution": source_df["predicted_grade"].value_counts().to_dict(),
            "avg_ph": round(source_df["ph"].mean(), 2),
            "avg_tds": round(source_df["tds_ppm"].mean(), 1),
            "avg_turbidity": round(source_df["turbidity_ntu"].mean(), 2),
            "avg_dissolved_o2": round(source_df["dissolved_oxygen_mg_l"].mean(), 2),
            "sample_count": len(source_df),
        }
    
    # Monthly trend
    df["month"] = df["timestamp"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["predicted_grade"].value_counts().unstack(fill_value=0)
    
    return {
        "overall_distribution": df["predicted_grade"].value_counts().to_dict(),
        "source_analysis": source_analysis,
        "monthly_trends": monthly.reset_index().to_dict(orient="records"),
        "treatment_guide": TREATMENT_RECOMMENDATIONS,
        "irrigation_limits": IRRIGATION_LIMITS,
        "recent_readings": df.tail(20)[["timestamp", "source_type", "ph", "tds_ppm",
                                         "turbidity_ntu", "predicted_grade"]].to_dict(orient="records"),
    }


def assess_irrigation_suitability(reading):
    """Assess if water is suitable for irrigation."""
    issues = []
    suitable = True
    
    for param, limits in IRRIGATION_LIMITS.items():
        value = reading.get(param)
        if value is None:
            continue
        if "max" in limits and value > limits["max"]:
            issues.append(f"{param} ({value}{limits['unit']}) exceeds limit ({limits['max']}{limits['unit']})")
            suitable = False
        if "min" in limits and value < limits["min"]:
            issues.append(f"{param} ({value}{limits['unit']}) below minimum ({limits['min']}{limits['unit']})")
            suitable = False
    
    return {
        "suitable": suitable,
        "issues": issues,
        "recommendation": "Suitable for irrigation" if suitable else "Treatment needed before irrigation",
    }


if __name__ == "__main__":
    train()
