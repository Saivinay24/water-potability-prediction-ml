"""
AgriSense AI — End-to-End Pipeline Runner
===========================================
Orchestrates the full ML pipeline: data generation → preprocessing →
model training → evaluation → export for dashboard.
"""

import os
import sys
import time
import json

# Add project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)


def run_pipeline():
    """Execute the complete AgriSense AI pipeline."""
    
    print("\n" + "=" * 70)
    print("   🌿 AgriSense AI — Full Pipeline Execution")
    print("=" * 70)
    
    start_time = time.time()
    all_metrics = {}
    
    # ── Step 1: Generate Synthetic Data ────────────────────────────────────
    print("\n" + "─" * 50)
    print("   📦 Step 1/6: Generating Synthetic Data")
    print("─" * 50)
    
    from data.generate_synthetic_data import main as generate_data
    generate_data()
    
    # ── Step 2: Train Soil Health Analyzer ─────────────────────────────────
    print("\n" + "─" * 50)
    print("   🌱 Step 2/6: Training Soil Health Analyzer")
    print("─" * 50)
    
    from models.soil_health.soil_analyzer import train as train_soil
    _, _, soil_metrics = train_soil()
    all_metrics["soil_health"] = soil_metrics
    
    # ── Step 3: Train Nutrient Deficiency Detector ────────────────────────
    print("\n" + "─" * 50)
    print("   🧪 Step 3/6: Training Nutrient Deficiency Detector")
    print("─" * 50)
    
    from models.soil_health.nutrient_deficiency import train as train_nutrients
    _, nutrient_metrics = train_nutrients()
    all_metrics["nutrient_deficiency"] = nutrient_metrics
    
    # ── Step 4: Train Water Quality Classifier ────────────────────────────
    print("\n" + "─" * 50)
    print("   💧 Step 4/6: Training Water Quality Classifier")
    print("─" * 50)
    
    from models.water_management.water_quality import train as train_water
    _, _, water_metrics = train_water()
    all_metrics["water_quality"] = water_metrics
    
    # ── Step 5: Train Irrigation Optimizer ────────────────────────────────
    print("\n" + "─" * 50)
    print("   💦 Step 5/6: Training Irrigation Optimizer")
    print("─" * 50)
    
    from models.water_management.irrigation_optimizer import train as train_irrigation
    _, irrigation_metrics = train_irrigation()
    all_metrics["irrigation"] = irrigation_metrics
    
    # ── Step 6: Train Crop Recommender ────────────────────────────────────
    print("\n" + "─" * 50)
    print("   🌾 Step 6/6: Training Crop Recommender & Yield Predictor")
    print("─" * 50)
    
    from models.crop_intelligence.crop_recommender import train as train_crops
    _, _, _, crop_metrics = train_crops()
    all_metrics["crop_recommendation"] = crop_metrics
    
    from models.crop_intelligence.yield_predictor import train as train_yield
    _, _, yield_metrics = train_yield()
    all_metrics["yield_prediction"] = yield_metrics
    
    # ── Summary ───────────────────────────────────────────────────────────
    elapsed = time.time() - start_time
    
    # Save combined metrics
    combined_path = os.path.join(PROJECT_ROOT, "results", "reports", "pipeline_summary.json")
    with open(combined_path, "w") as f:
        json.dump(all_metrics, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("   ✅ Pipeline Complete!")
    print("=" * 70)
    print(f"\n   ⏱️  Total time: {elapsed:.1f}s")
    print(f"   📊 Models trained: 6")
    print(f"   💾 Results saved to: results/")
    print(f"   🌐 Dashboard data: results/predictions/")
    print(f"\n   Open dashboard/index.html to view results")
    print("=" * 70 + "\n")
    
    return all_metrics


if __name__ == "__main__":
    run_pipeline()
