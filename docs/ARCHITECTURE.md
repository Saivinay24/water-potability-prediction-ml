# AgriSense AI — System Architecture

## Overview

AgriSense AI follows a **layered pipeline architecture** where data flows from physical sensors through preprocessing, ML inference, and into a visualization dashboard.

```mermaid
graph TB
    subgraph Sensors["🔌 Sensor Layer"]
        S1["Soil Sensors<br/>NPK, pH, Moisture, EC, Temp"]
        S2["Water Sensors<br/>pH, TDS, Turbidity, DO"]
        S3["Weather Station<br/>Temp, Humidity, Rain, Wind"]
    end

    subgraph Pipeline["⚙️ Data Pipeline"]
        P1["Data Ingestion<br/>(CSV / MQTT)"]
        P2["Cleaning & Imputation"]
        P3["Feature Engineering"]
    end

    subgraph Models["🧠 ML Models"]
        M1["Soil Health Analyzer<br/>RF + GBR Ensemble"]
        M2["Nutrient Deficiency<br/>Multi-Output RF"]
        M3["Water Quality<br/>Gradient Boosting"]
        M4["Irrigation Optimizer<br/>GBR + Rules"]
        M5["Crop Recommender<br/>RF + KNN + GB"]
        M6["Yield Predictor<br/>Gradient Boosting"]
    end

    subgraph Output["📊 Output Layer"]
        O1["JSON Predictions"]
        O2["Metrics Reports"]
        O3["Web Dashboard"]
    end

    S1 --> P1
    S2 --> P1
    S3 --> P1
    P1 --> P2 --> P3
    P3 --> M1 & M2 & M3 & M4 & M5 & M6
    M1 & M2 --> O1
    M3 & M4 --> O1
    M5 & M6 --> O1
    O1 --> O3
    M1 & M2 & M3 & M4 & M5 & M6 --> O2
```

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ML Framework | scikit-learn | Well-documented, production-ready, sufficient for tabular data |
| Ensemble Method | Voting (RF + GBR) | Combines stability of RF with gradient boosting accuracy |
| Class Balancing | Sample weights | Simpler than SMOTE, avoids synthetic minority samples |
| Dashboard | Vanilla HTML/CSS/JS | Zero build tools, opens anywhere, no Node.js needed |
| Charts | Chart.js (CDN) | Lightweight, responsive, great dark theme support |
| Data Format | CSV → JSON | CSV for training, JSON for dashboard consumption |

## Data Flow

### Training Flow
```
Sensors → CSV files (data/raw/)
         → Preprocessing (models/utils/preprocessing.py)
         → Feature engineering (NPK ratios, ETo, heat index)
         → Train/Test split (80/20)
         → Model training with cross-validation
         → Metrics saved (results/reports/)
         → Predictions exported (results/predictions/)
```

### Inference Flow
```
New sensor reading (dict)
         → Load saved model (.joblib)
         → Scale features with saved scaler
         → Model.predict()
         → Post-process (categorize, recommend)
         → Return JSON response
```

## Module Dependency Graph

```mermaid
graph LR
    A["generate_synthetic_data.py"] --> B["data/raw/*.csv"]
    B --> C["preprocessing.py"]
    C --> D["soil_analyzer.py"]
    C --> E["nutrient_deficiency.py"]
    C --> F["water_quality.py"]
    C --> G["irrigation_optimizer.py"]
    C --> H["crop_recommender.py"]
    C --> I["yield_predictor.py"]
    D & E & F & G & H & I --> J["evaluation.py"]
    J --> K["results/reports/"]
    D & E & F & G & H & I --> L["results/predictions/"]
    L --> M["dashboard/"]
```

## Zone Architecture

The farm is divided into 8 sensor zones, each with distinct soil characteristics:

| Zone | Soil Type | Characteristics | Assigned Crop |
|------|-----------|----------------|---------------|
| Zone 1 | Loamy | Balanced, high retention | Rice |
| Zone 2 | Clay | Heavy, waterlogged risk | Wheat |
| Zone 3 | Sandy | Low retention, drains fast | Maize |
| Zone 4 | Silt | Good nutrients, moderate | Soybean |
| Zone 5 | Loamy | Nutrient-rich, productive | Cotton |
| Zone 6 | Clay Loam | Heavy but fertile | Sugarcane |
| Zone 7 | Sandy Loam | Light, needs frequent water | Potato |
| Zone 8 | Peaty | Organic-rich, acidic | Tomato |
