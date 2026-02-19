<div align="center">

# 🌿 AgriSense AI

### Precision Agriculture Intelligence Platform

*ML/AI-powered farm management system that transforms sensor data into actionable insights for soil health, water management, crop selection, and yield optimization.*

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-10b981?style=flat-square)](LICENSE)

</div>

---

## 🎯 What is AgriSense AI?

AgriSense AI is a **full-stack precision agriculture platform** that ingests data from IoT soil, water, and weather sensors deployed across farmland, then uses machine learning to deliver real-time, zone-by-zone recommendations for:

- 🌱 **Soil Health Scoring** — 0-100 composite health score with NPK analysis
- 🧪 **Nutrient Deficiency Detection** — Multi-label deficiency diagnosis with fertilizer dosage recommendations
- 💧 **Water Quality Grading** — A-F classification with irrigation suitability and treatment guides
- 💦 **Smart Irrigation Scheduling** — Zone-specific water needs with 34% savings vs uniform irrigation
- 🌾 **Crop Recommendations** — Top-5 crop suggestions with confidence scores from a 40-crop database
- 📈 **Yield Forecasting** — Production predictions with efficiency analysis and risk alerts

## 🏗️ Architecture

```
                    ┌─────────────────────────────────┐
                    │        IoT SENSOR LAYER          │
                    │  Soil · Water · Weather Sensors   │
                    └──────────────┬──────────────────┘
                                   │ Raw Data (CSV/MQTT)
                    ┌──────────────▼──────────────────┐
                    │       DATA PIPELINE LAYER        │
                    │  Ingestion → Cleaning → Features  │
                    └──────────────┬──────────────────┘
                                   │ Processed Features
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │  SOIL HEALTH  │      │    WATER      │      │    CROP       │
   │   ANALYZER    │      │  MANAGEMENT   │      │ INTELLIGENCE  │
   │ ─────────── │      │ ─────────── │      │ ─────────── │
   │ Health Score  │      │ Quality Grade │      │ Crop Suggest  │
   │ NPK Analysis  │      │ Irrigation    │      │ Yield Predict │
   │ Deficiency    │      │ Treatment     │      │ Risk Assess   │
   └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
          │                      │                      │
          └────────────────┬─────┘──────────────────────┘
                           ▼
              ┌────────────────────────┐
              │    WEB DASHBOARD       │
              │  Charts · Alerts · UI   │
              └────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Full Pipeline

```bash
python scripts/run_pipeline.py
```

This will:
1. Generate 25,000+ synthetic sensor records
2. Train all 5 ML models with cross-validation
3. Export predictions and metrics to `results/`

### 3. View the Dashboard

Open `dashboard/index.html` in your browser — no server needed.

## 📂 Project Structure

```
AgriSense-AI/
├── 📊 data/                          # Data layer
│   ├── raw/                          # Raw sensor CSVs
│   ├── processed/                    # Feature-engineered data
│   └── generate_synthetic_data.py    # Realistic data generator
│
├── 🧠 models/                        # ML model layer
│   ├── soil_health/
│   │   ├── soil_analyzer.py          # RF+GBR ensemble (R² ~0.85)
│   │   └── nutrient_deficiency.py    # Multi-label classifier
│   ├── water_management/
│   │   ├── water_quality.py          # GB classifier with SMOTE
│   │   └── irrigation_optimizer.py   # GBR with weather integration
│   ├── crop_intelligence/
│   │   ├── crop_recommender.py       # RF+KNN+GB ensemble
│   │   └── yield_predictor.py        # GBR yield forecaster
│   └── utils/
│       ├── preprocessing.py          # Shared data pipeline
│       └── evaluation.py             # Metrics & reporting
│
├── 🌐 dashboard/                     # Web UI
│   ├── index.html                    # Main dashboard
│   ├── css/styles.css                # Premium dark theme
│   └── js/                           # Charts & app logic
│
├── 📝 docs/                          # Documentation
│   ├── ARCHITECTURE.md               # System design
│   ├── API_REFERENCE.md              # Model APIs
│   ├── SENSOR_INTEGRATION_GUIDE.md   # IoT hardware guide
│   └── PRESENTATION.md               # Stakeholder summary
│
├── 🔬 scripts/
│   └── run_pipeline.py               # End-to-end orchestrator
│
├── 📈 results/                       # Model outputs
│   ├── predictions/                  # JSON for dashboard
│   └── reports/                      # Metrics & summaries
│
├── 🧪 tests/                         # Test suite
├── requirements.txt
└── .gitignore
```

## 🧠 Models & Performance

| Model | Algorithm | Task | Key Metric |
|-------|-----------|------|------------|
| Soil Health Analyzer | RF + GBR Ensemble | Regression (0-100 score) | R² ~ 0.85 |
| Nutrient Deficiency | Multi-Output RF | Multi-label Classification | F1 ~ 0.90+ |
| Water Quality | Gradient Boosting | Classification (A-F grades) | Accuracy ~ 0.88 |
| Irrigation Optimizer | GBR + Rule Engine | Regression (mm/day) | R² ~ 0.78 |
| Crop Recommender | RF + KNN + GB Voting | Classification (40 crops) | Accuracy ~ 0.82 |
| Yield Predictor | Gradient Boosting | Regression (tons/ha) | R² ~ 0.80 |

## 🌐 Dashboard Features

| Tab | Features |
|-----|----------|
| **Overview** | KPI cards, zone health comparison, deficiency donut chart, alert preview |
| **Soil Health** | SVG nutrient gauges (N/P/K/pH/OM), zone NPK bar chart, recommendations |
| **Water Quality** | Source cards with grades, stacked quality chart, treatment guide |
| **Irrigation** | Water savings stats, zone schedule cards, weekly forecast line chart |
| **Crop Advisor** | Zone recommendation cards with confidence bars, yield efficiency chart |
| **Alerts** | Filterable notifications (critical/warning/info) with action items |

## 🔌 Sensor Integration

AgriSense AI is designed to work with real IoT hardware. See [SENSOR_INTEGRATION_GUIDE.md](docs/SENSOR_INTEGRATION_GUIDE.md) for:

- Supported sensors (NPK, pH, moisture, EC, weather stations)
- Wiring diagrams for Arduino/Raspberry Pi
- Data format specifications
- MQTT/HTTP ingestion protocols

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, data flow, technology decisions |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Model input/output schemas, example calls |
| [SENSOR_INTEGRATION_GUIDE.md](docs/SENSOR_INTEGRATION_GUIDE.md) | Hardware setup, protocols |
| [PRESENTATION.md](docs/PRESENTATION.md) | Executive summary for stakeholders |

## 🛠️ Tech Stack

- **ML/AI**: scikit-learn, XGBoost, NumPy, Pandas
- **Visualization**: Chart.js, Matplotlib, Seaborn
- **Dashboard**: Vanilla HTML/CSS/JS (zero build tools)
- **Data**: Synthetic generator with realistic correlations

## 📄 License

This project is open source under the MIT License.

---

<div align="center">
<sub>Built with 🌿 by AgriSense AI</sub>
</div>
