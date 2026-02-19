# AgriSense AI — API Reference

## Model APIs

All models provide a `train()` function for training and a `predict()`/`diagnose()`/`recommend()` function for inference.

---

## 1. Soil Health Analyzer

### `soil_analyzer.train(data_path=None, save_model=True)`

Trains the RF+GBR ensemble on soil sensor data.

**Returns**: `(model, scaler, metrics)`

### `soil_analyzer.predict(sensor_reading, model_path=None)`

**Input**:
```python
sensor_reading = {
    "nitrogen_mg_kg": 82.5,
    "phosphorus_mg_kg": 45.2,
    "potassium_mg_kg": 63.8,
    "ph": 6.5,
    "organic_matter_pct": 4.2,
    "moisture_pct": 34.1,
    "soil_temperature_c": 28.3,
    "ec_mscm": 1.8,
    "npk_ratio": 0.76,        # auto-computed if missing
    "nutrient_total": 191.5,    # auto-computed if missing
}
```

**Output**:
```python
{
    "score": 78.2,
    "category": "Good",  # Excellent/Good/Fair/Poor
    "recommendations": [
        "✅ Soil health is good. Maintain current practices."
    ]
}
```

---

## 2. Nutrient Deficiency Detector

### `nutrient_deficiency.train(data_path=None, save_model=True)`

Trains the multi-label RF classifier.

**Returns**: `(model, metrics)`

### `nutrient_deficiency.diagnose(sensor_reading)`

**Input**: Same soil reading dict as above.

**Output**:
```python
{
    "deficiencies": [
        {"nutrient": "Phosphorus", "value": 18, "severity": "Critical"},
        {"nutrient": "Potassium", "value": 28, "severity": "Low"},
    ],
    "severity": "critical",  # overall: critical/moderate/none
    "recommendations": [
        {"amendment": "DAP (18-46-0)", "dosage": "50-80 kg/ha", "timing": "Apply at sowing as basal dose"},
        {"amendment": "SSP (0-16-0)", "dosage": "150-250 kg/ha", "timing": "Basal application"},
        {"amendment": "MOP - Muriate of Potash (0-0-60)", "dosage": "40-80 kg/ha", "timing": "Basal or split application"},
    ]
}
```

---

## 3. Water Quality Classifier

### `water_quality.train(data_path=None, save_model=True)`

Trains the Gradient Boosting classifier.

**Returns**: `(model, label_encoder, metrics)`

### `water_quality.assess_irrigation_suitability(reading)`

**Input**:
```python
reading = {
    "ph": 7.5,
    "tds_ppm": 602.3,
    "chloride_mg_l": 98.5,
    "sulfate_mg_l": 78.2,
    "hardness_mg_l": 245.0,
}
```

**Output**:
```python
{
    "suitable": True,
    "issues": [],
    "recommendation": "Suitable for irrigation"
}
```

---

## 4. Irrigation Optimizer

### `irrigation_optimizer.train(save_model=True)`

Trains the GBR model on merged soil + weather + crop data.

**Returns**: `(model, metrics)`

---

## 5. Crop Recommender

### `crop_recommender.train(save_model=True)`

Trains the RF+KNN+GB ensemble.

**Returns**: `(model, scaler, label_encoder, metrics)`

### `crop_recommender.recommend(soil_reading, top_n=5)`

**Input**: Soil sensor reading dict.

**Output**:
```python
[
    {"crop": "Rice", "confidence": 89.2, "expected_yield_tons_ha": 4.5, "water_requirement_mm": 1200, "growing_season": "Kharif"},
    {"crop": "Sugarcane", "confidence": 72.1, "expected_yield_tons_ha": 70.0, "water_requirement_mm": 1500, "growing_season": "Annual"},
    {"crop": "Banana", "confidence": 68.5, "expected_yield_tons_ha": 40.0, "water_requirement_mm": 1200, "growing_season": "Annual"},
]
```

---

## 6. Yield Predictor

### `yield_predictor.train(save_model=True)`

Trains the GBR model on merged soil + weather + crop data.

**Returns**: `(model, scaler, metrics)`

---

## Pipeline Runner

### `scripts/run_pipeline.py`

Orchestrates all 6 steps in sequence:

```bash
python scripts/run_pipeline.py
```

Outputs:
- `results/reports/pipeline_summary.json` — Combined metrics
- `results/reports/*_metrics.json` — Per-model metrics
- `results/predictions/*_predictions.json` — Dashboard data

---

## Evaluation Metrics Format

### Classification Models
```json
{
    "model_name": "Water Quality Classifier",
    "accuracy": 0.8835,
    "precision_weighted": 0.8842,
    "recall_weighted": 0.8835,
    "f1_weighted": 0.8838,
    "n_samples": 2000
}
```

### Regression Models
```json
{
    "model_name": "Soil Health Analyzer",
    "mae": 3.24,
    "rmse": 4.58,
    "r2_score": 0.8521,
    "mape": 5.62,
    "n_samples": 2000
}
```
