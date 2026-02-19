"""
AgriSense AI — Model Evaluation Utilities
==========================================
Shared evaluation and reporting functions for all ML models.
"""

import numpy as np
import json
import os
from datetime import datetime
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)


def evaluate_classifier(y_true, y_pred, model_name, labels=None):
    """
    Comprehensive evaluation for classification models.
    
    Returns a dict with all metrics and a formatted report string.
    """
    report = classification_report(y_true, y_pred, labels=labels, output_dict=True)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    metrics = {
        "model_name": model_name,
        "timestamp": datetime.now().isoformat(),
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision_weighted": round(precision_score(y_true, y_pred, average="weighted", zero_division=0), 4),
        "recall_weighted": round(recall_score(y_true, y_pred, average="weighted", zero_division=0), 4),
        "f1_weighted": round(f1_score(y_true, y_pred, average="weighted", zero_division=0), 4),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "n_samples": len(y_true),
    }
    
    # Print formatted report
    print(f"\n{'='*60}")
    print(f"  📊 {model_name} — Classification Report")
    print(f"{'='*60}")
    print(classification_report(y_true, y_pred, labels=labels))
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  F1 Score:  {metrics['f1_weighted']:.4f}")
    print(f"{'='*60}\n")
    
    return metrics


def evaluate_regressor(y_true, y_pred, model_name):
    """
    Comprehensive evaluation for regression models.
    
    Returns a dict with all metrics.
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
    
    metrics = {
        "model_name": model_name,
        "timestamp": datetime.now().isoformat(),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2_score": round(r2, 4),
        "mape": round(mape, 2),
        "n_samples": len(y_true),
    }
    
    print(f"\n{'='*60}")
    print(f"  📊 {model_name} — Regression Report")
    print(f"{'='*60}")
    print(f"  MAE:     {mae:.4f}")
    print(f"  RMSE:    {rmse:.4f}")
    print(f"  R²:      {r2:.4f}")
    print(f"  MAPE:    {mape:.2f}%")
    print(f"{'='*60}\n")
    
    return metrics


def save_metrics(metrics, output_dir):
    """Save metrics to a JSON file in the reports directory."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{metrics['model_name'].lower().replace(' ', '_')}_metrics.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    
    print(f"  💾 Metrics saved to {filepath}")
    return filepath


def save_predictions(predictions, output_dir, model_name):
    """Save model predictions to JSON for dashboard consumption."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{model_name.lower().replace(' ', '_')}_predictions.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w") as f:
        json.dump(predictions, f, indent=2, default=str)
    
    print(f"  💾 Predictions saved to {filepath}")
    return filepath


def get_feature_importance(model, feature_names, top_n=10):
    """Extract and rank feature importances from tree-based models."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_).flatten()
    else:
        return {}
    
    indices = np.argsort(importances)[::-1][:top_n]
    
    result = {}
    for i in indices:
        if i < len(feature_names):
            result[feature_names[i]] = round(float(importances[i]), 4)
    
    return result
