"""
AgriSense AI — Synthetic Agricultural Data Generator
=====================================================
Generates realistic sensor data for soil, water, weather, and crop databases
with temporal correlations, spatial zones, and cross-dataset relationships.
"""

import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta

# Reproducibility
np.random.seed(42)

# ─── Configuration ────────────────────────────────────────────────────────────

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")

SOIL_RECORDS = 10_000
WATER_RECORDS = 10_000
WEATHER_RECORDS = 5_000
NUM_ZONES = 8

ZONE_PROFILES = {
    "Zone_1": {"soil_type": "Loamy", "base_pH": 6.5, "base_N": 80, "base_P": 45, "base_K": 60, "base_moisture": 35},
    "Zone_2": {"soil_type": "Clay", "base_pH": 7.2, "base_N": 60, "base_P": 35, "base_K": 50, "base_moisture": 45},
    "Zone_3": {"soil_type": "Sandy", "base_pH": 5.8, "base_N": 40, "base_P": 20, "base_K": 35, "base_moisture": 15},
    "Zone_4": {"soil_type": "Silt", "base_pH": 6.8, "base_N": 70, "base_P": 40, "base_K": 55, "base_moisture": 40},
    "Zone_5": {"soil_type": "Loamy", "base_pH": 6.2, "base_N": 90, "base_P": 50, "base_K": 70, "base_moisture": 32},
    "Zone_6": {"soil_type": "Clay Loam", "base_pH": 7.0, "base_N": 55, "base_P": 30, "base_K": 45, "base_moisture": 42},
    "Zone_7": {"soil_type": "Sandy Loam", "base_pH": 6.0, "base_N": 50, "base_P": 25, "base_K": 40, "base_moisture": 22},
    "Zone_8": {"soil_type": "Peaty", "base_pH": 5.5, "base_N": 100, "base_P": 55, "base_K": 75, "base_moisture": 55},
}


# ─── Soil Sensor Data ─────────────────────────────────────────────────────────

def generate_soil_data(n_records=SOIL_RECORDS):
    """
    Generate soil sensor readings with zone-specific profiles and seasonal variation.
    
    Features:
    - Nitrogen (N), Phosphorus (P), Potassium (K) in mg/kg
    - pH level
    - Organic Matter (%)
    - Moisture (%)
    - Temperature (°C) — soil temperature
    - Electrical Conductivity (mS/cm)
    - Zone ID and Soil Type
    - Timestamp with seasonal patterns
    """
    print("  🌱 Generating soil sensor data...")
    
    # Generate timestamps spanning 2 years
    start_date = datetime(2024, 1, 1)
    timestamps = [start_date + timedelta(hours=np.random.randint(0, 365 * 2 * 24)) for _ in range(n_records)]
    timestamps.sort()
    
    # Assign zones
    zones = np.random.choice(list(ZONE_PROFILES.keys()), n_records)
    
    records = []
    for i, (ts, zone) in enumerate(zip(timestamps, zones)):
        profile = ZONE_PROFILES[zone]
        
        # Seasonal factor (0-1, peaks in monsoon/summer)
        day_of_year = ts.timetuple().tm_yday
        seasonal = 0.5 + 0.5 * np.sin(2 * np.pi * (day_of_year - 80) / 365)  # Peak ~June
        
        # Seasonal moisture boost (monsoon effect)
        moisture_seasonal = 0.3 + 0.7 * np.sin(2 * np.pi * (day_of_year - 150) / 365)
        moisture_seasonal = max(0.1, moisture_seasonal)
        
        record = {
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "zone_id": zone,
            "soil_type": profile["soil_type"],
            "nitrogen_mg_kg": max(5, profile["base_N"] * (0.7 + 0.6 * seasonal) + np.random.normal(0, 12)),
            "phosphorus_mg_kg": max(2, profile["base_P"] * (0.8 + 0.4 * seasonal) + np.random.normal(0, 8)),
            "potassium_mg_kg": max(5, profile["base_K"] * (0.75 + 0.5 * seasonal) + np.random.normal(0, 10)),
            "ph": np.clip(profile["base_pH"] + np.random.normal(0, 0.3), 4.0, 9.0),
            "organic_matter_pct": np.clip(np.random.normal(3.5, 1.2) + (1 if profile["soil_type"] == "Peaty" else 0), 0.5, 12.0),
            "moisture_pct": np.clip(profile["base_moisture"] * moisture_seasonal + np.random.normal(0, 5), 2, 80),
            "soil_temperature_c": np.clip(15 + 15 * seasonal + np.random.normal(0, 3), 5, 45),
            "ec_mscm": np.clip(np.random.normal(1.5, 0.6), 0.1, 5.0),
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    
    # Inject ~3% missing values in some columns (simulating sensor failures)
    for col in ["nitrogen_mg_kg", "phosphorus_mg_kg", "ec_mscm"]:
        mask = np.random.random(n_records) < 0.03
        df.loc[mask, col] = np.nan
    
    return df


# ─── Water Quality Data ───────────────────────────────────────────────────────

def generate_water_data(n_records=WATER_RECORDS):
    """
    Generate water quality sensor readings.
    
    Features:
    - pH, TDS (ppm), Turbidity (NTU), Dissolved O₂ (mg/L)
    - Hardness (mg/L), Chloride (mg/L), Sulfate (mg/L), Nitrate (mg/L)
    - Temperature (°C)
    - Source type (Borewell, River, Canal, Rainwater)
    - Quality class (A/B/C/D/F)
    """
    print("  💧 Generating water quality data...")
    
    start_date = datetime(2024, 1, 1)
    timestamps = [start_date + timedelta(hours=np.random.randint(0, 365 * 2 * 24)) for _ in range(n_records)]
    timestamps.sort()
    
    sources = np.random.choice(
        ["Borewell", "River", "Canal", "Rainwater"],
        n_records,
        p=[0.35, 0.25, 0.25, 0.15]
    )
    
    records = []
    for ts, source in zip(timestamps, sources):
        day_of_year = ts.timetuple().tm_yday
        seasonal = 0.5 + 0.5 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Source-specific baselines
        source_factors = {
            "Borewell":  {"ph": 7.5, "tds": 600, "turb": 2,  "do": 5, "hard": 250, "cl": 100, "so4": 80,  "no3": 15},
            "River":     {"ph": 7.0, "tds": 350, "turb": 15, "do": 7, "hard": 150, "cl": 50,  "so4": 40,  "no3": 25},
            "Canal":     {"ph": 7.2, "tds": 450, "turb": 20, "do": 6, "hard": 180, "cl": 70,  "so4": 55,  "no3": 30},
            "Rainwater": {"ph": 6.5, "tds": 50,  "turb": 3,  "do": 8, "hard": 30,  "cl": 10,  "so4": 10,  "no3": 5},
        }
        f = source_factors[source]
        
        ph = np.clip(f["ph"] + np.random.normal(0, 0.4), 4.5, 9.5)
        tds = max(10, f["tds"] + np.random.normal(0, f["tds"] * 0.2))
        turbidity = max(0.1, f["turb"] * (1 + 0.5 * seasonal) + np.random.normal(0, f["turb"] * 0.3))
        dissolved_o2 = np.clip(f["do"] + np.random.normal(0, 1.2), 1, 14)
        hardness = max(10, f["hard"] + np.random.normal(0, f["hard"] * 0.15))
        chloride = max(1, f["cl"] + np.random.normal(0, f["cl"] * 0.2))
        sulfate = max(1, f["so4"] + np.random.normal(0, f["so4"] * 0.2))
        nitrate = max(0.5, f["no3"] * (1 + 0.3 * seasonal) + np.random.normal(0, f["no3"] * 0.25))
        temp = np.clip(20 + 10 * seasonal + np.random.normal(0, 3), 8, 38)
        
        # Derive quality grade based on WHO guidelines
        score = 0
        if 6.5 <= ph <= 8.5: score += 20
        elif 6.0 <= ph <= 9.0: score += 10
        if tds < 500: score += 20
        elif tds < 1000: score += 10
        if turbidity < 5: score += 20
        elif turbidity < 10: score += 10
        if dissolved_o2 > 6: score += 20
        elif dissolved_o2 > 4: score += 10
        if nitrate < 10: score += 20
        elif nitrate < 45: score += 10
        
        if score >= 80: grade = "A"
        elif score >= 60: grade = "B"
        elif score >= 40: grade = "C"
        elif score >= 20: grade = "D"
        else: grade = "F"
        
        records.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "source_type": source,
            "ph": round(ph, 2),
            "tds_ppm": round(tds, 1),
            "turbidity_ntu": round(turbidity, 2),
            "dissolved_oxygen_mg_l": round(dissolved_o2, 2),
            "hardness_mg_l": round(hardness, 1),
            "chloride_mg_l": round(chloride, 1),
            "sulfate_mg_l": round(sulfate, 1),
            "nitrate_mg_l": round(nitrate, 2),
            "water_temperature_c": round(temp, 1),
            "quality_grade": grade,
        })
    
    df = pd.DataFrame(records)
    
    # Inject ~2% missing values
    for col in ["turbidity_ntu", "dissolved_oxygen_mg_l"]:
        mask = np.random.random(n_records) < 0.02
        df.loc[mask, col] = np.nan
    
    return df


# ─── Weather Data ──────────────────────────────────────────────────────────────

def generate_weather_data(n_records=WEATHER_RECORDS):
    """
    Generate weather station data with realistic patterns.
    
    Features:
    - Temperature (°C), Humidity (%), Rainfall (mm)
    - Wind Speed (km/h), Solar Radiation (W/m²)
    - Atmospheric Pressure (hPa), UV Index
    """
    print("  🌤️ Generating weather station data...")
    
    start_date = datetime(2024, 1, 1)
    timestamps = [start_date + timedelta(hours=i * (365 * 2 * 24 // n_records)) for i in range(n_records)]
    
    records = []
    for ts in timestamps:
        day_of_year = ts.timetuple().tm_yday
        hour = ts.hour
        
        # Seasonal patterns
        seasonal = 0.5 + 0.5 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        # Diurnal pattern
        diurnal = 0.5 + 0.5 * np.sin(2 * np.pi * (hour - 6) / 24)
        
        temp = 15 + 20 * seasonal + 5 * diurnal + np.random.normal(0, 2)
        humidity = np.clip(60 + 25 * (1 - seasonal) * (1 - 0.3 * diurnal) + np.random.normal(0, 8), 15, 100)
        
        # Monsoon rainfall pattern (peaks July-September for Indian agriculture)
        monsoon_factor = np.exp(-0.5 * ((day_of_year - 210) / 40) ** 2)
        rainfall = max(0, np.random.exponential(5 * monsoon_factor + 0.5))
        if np.random.random() > 0.3 + 0.4 * monsoon_factor:  # Non-rainy day probability
            rainfall = 0
        
        wind_speed = max(0, np.random.weibull(2) * 8 + 3)
        solar_radiation = max(0, 300 * diurnal * (0.7 + 0.3 * seasonal) * np.random.uniform(0.5, 1.2))
        pressure = np.random.normal(1013, 5)
        uv_index = max(0, round(8 * diurnal * seasonal + np.random.normal(0, 1)))
        
        records.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_c": round(temp, 1),
            "humidity_pct": round(humidity, 1),
            "rainfall_mm": round(rainfall, 1),
            "wind_speed_kmh": round(wind_speed, 1),
            "solar_radiation_wm2": round(solar_radiation, 1),
            "pressure_hpa": round(pressure, 1),
            "uv_index": int(np.clip(uv_index, 0, 12)),
        })
    
    return pd.DataFrame(records)


# ─── Crop Database ─────────────────────────────────────────────────────────────

def generate_crop_database():
    """
    Generate a reference database of crops with their ideal growing conditions.
    """
    print("  🌾 Generating crop reference database...")
    
    crops = [
        # (name, N_min, N_max, P_min, P_max, K_min, K_max, pH_min, pH_max, water_need_mm, temp_min, temp_max, season, yield_tons_ha)
        ("Rice", 80, 120, 40, 60, 40, 80, 5.5, 7.0, 1200, 20, 35, "Kharif", 4.5),
        ("Wheat", 60, 100, 30, 50, 30, 60, 6.0, 7.5, 450, 15, 25, "Rabi", 3.5),
        ("Maize", 70, 120, 35, 55, 35, 70, 5.5, 7.5, 600, 18, 35, "Kharif", 5.0),
        ("Soybean", 20, 40, 40, 60, 40, 60, 6.0, 7.0, 500, 20, 30, "Kharif", 2.5),
        ("Cotton", 60, 100, 30, 50, 30, 50, 6.0, 8.0, 700, 20, 35, "Kharif", 2.0),
        ("Sugarcane", 80, 150, 40, 70, 60, 100, 6.0, 8.0, 1500, 20, 38, "Annual", 70.0),
        ("Potato", 60, 100, 50, 80, 60, 100, 5.5, 6.5, 500, 15, 25, "Rabi", 25.0),
        ("Tomato", 80, 120, 50, 80, 60, 100, 6.0, 7.0, 600, 18, 30, "Year-round", 30.0),
        ("Onion", 50, 80, 40, 60, 40, 60, 6.0, 7.5, 400, 15, 30, "Rabi", 20.0),
        ("Groundnut", 20, 40, 40, 80, 30, 50, 6.0, 7.0, 500, 22, 35, "Kharif", 2.0),
        ("Mustard", 40, 60, 20, 40, 20, 40, 6.0, 7.5, 300, 10, 25, "Rabi", 1.8),
        ("Chickpea", 20, 30, 40, 60, 30, 50, 6.0, 8.0, 350, 10, 30, "Rabi", 1.5),
        ("Pigeon Pea", 20, 40, 40, 60, 20, 40, 5.5, 7.5, 600, 20, 35, "Kharif", 1.2),
        ("Barley", 50, 80, 25, 45, 25, 50, 6.0, 8.0, 400, 12, 25, "Rabi", 3.0),
        ("Millet", 40, 60, 20, 35, 20, 40, 5.5, 7.5, 350, 25, 40, "Kharif", 1.5),
        ("Sorghum", 50, 80, 25, 40, 25, 50, 5.5, 8.0, 450, 25, 40, "Kharif", 2.5),
        ("Lentil", 20, 30, 40, 60, 25, 40, 6.0, 7.5, 300, 10, 25, "Rabi", 1.2),
        ("Sunflower", 60, 90, 30, 50, 30, 60, 6.0, 7.5, 500, 18, 30, "Kharif", 2.0),
        ("Sesame", 30, 50, 20, 40, 20, 40, 5.5, 8.0, 400, 25, 35, "Kharif", 0.8),
        ("Jute", 50, 70, 25, 40, 25, 50, 5.5, 7.0, 1000, 25, 38, "Kharif", 2.5),
        ("Tea", 70, 120, 30, 50, 40, 60, 4.5, 5.5, 1500, 15, 30, "Annual", 2.0),
        ("Coffee", 60, 100, 30, 50, 50, 80, 6.0, 6.5, 1200, 15, 28, "Annual", 1.5),
        ("Coconut", 50, 80, 30, 50, 80, 120, 5.5, 7.0, 1500, 20, 35, "Annual", 8.0),
        ("Banana", 80, 120, 40, 60, 100, 150, 6.0, 7.5, 1200, 20, 35, "Annual", 40.0),
        ("Mango", 60, 100, 30, 50, 50, 80, 5.5, 7.5, 800, 22, 38, "Annual", 10.0),
        ("Turmeric", 60, 90, 30, 50, 80, 120, 5.5, 7.0, 1200, 20, 35, "Kharif", 8.0),
        ("Ginger", 70, 100, 40, 60, 60, 90, 5.5, 6.5, 1500, 20, 30, "Kharif", 5.0),
        ("Chili", 60, 100, 40, 60, 40, 60, 6.0, 7.0, 600, 20, 35, "Kharif", 3.0),
        ("Garlic", 50, 80, 40, 60, 40, 60, 6.0, 7.5, 400, 12, 25, "Rabi", 8.0),
        ("Cabbage", 80, 120, 40, 60, 60, 80, 6.0, 7.0, 400, 15, 25, "Rabi", 30.0),
        ("Carrot", 50, 80, 40, 60, 50, 70, 6.0, 6.8, 400, 12, 25, "Rabi", 25.0),
        ("Spinach", 60, 100, 40, 60, 50, 70, 6.0, 7.5, 350, 10, 25, "Rabi", 15.0),
        ("Peas", 20, 30, 40, 60, 30, 50, 6.0, 7.5, 400, 10, 25, "Rabi", 5.0),
        ("Cauliflower", 80, 120, 50, 70, 50, 80, 6.0, 7.0, 450, 15, 25, "Rabi", 25.0),
        ("Brinjal", 60, 100, 40, 60, 50, 80, 5.5, 6.5, 500, 20, 35, "Year-round", 20.0),
        ("Okra", 50, 80, 30, 50, 30, 50, 6.0, 7.0, 500, 22, 38, "Kharif", 10.0),
        ("Cucumber", 50, 80, 40, 60, 50, 80, 5.5, 7.0, 500, 18, 35, "Kharif", 15.0),
        ("Watermelon", 60, 80, 40, 60, 50, 80, 6.0, 7.0, 500, 22, 35, "Kharif", 20.0),
        ("Papaya", 80, 120, 40, 60, 80, 120, 6.0, 7.0, 1200, 22, 35, "Annual", 30.0),
        ("Guava", 50, 80, 30, 50, 40, 60, 5.5, 7.5, 800, 20, 35, "Annual", 15.0),
    ]
    
    records = []
    for crop in crops:
        name, n_min, n_max, p_min, p_max, k_min, k_max, ph_min, ph_max, water, t_min, t_max, season, yield_t = crop
        records.append({
            "crop_name": name,
            "nitrogen_min_mg_kg": n_min,
            "nitrogen_max_mg_kg": n_max,
            "phosphorus_min_mg_kg": p_min,
            "phosphorus_max_mg_kg": p_max,
            "potassium_min_mg_kg": k_min,
            "potassium_max_mg_kg": k_max,
            "ph_min": ph_min,
            "ph_max": ph_max,
            "water_requirement_mm": water,
            "temperature_min_c": t_min,
            "temperature_max_c": t_max,
            "growing_season": season,
            "expected_yield_tons_per_ha": yield_t,
        })
    
    return pd.DataFrame(records)


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    """Generate all datasets and save to CSV files."""
    print("\n🚀 AgriSense AI — Synthetic Data Generator")
    print("=" * 50)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate all datasets
    soil_df = generate_soil_data()
    water_df = generate_water_data()
    weather_df = generate_weather_data()
    crop_df = generate_crop_database()
    
    # Save to CSV
    soil_path = os.path.join(OUTPUT_DIR, "soil_sensors.csv")
    water_path = os.path.join(OUTPUT_DIR, "water_quality.csv")
    weather_path = os.path.join(OUTPUT_DIR, "weather_data.csv")
    crop_path = os.path.join(OUTPUT_DIR, "crop_database.csv")
    
    soil_df.to_csv(soil_path, index=False)
    water_df.to_csv(water_path, index=False)
    weather_df.to_csv(weather_path, index=False)
    crop_df.to_csv(crop_path, index=False)
    
    print(f"\n✅ Data generated successfully!")
    print(f"   📊 Soil sensors:    {len(soil_df):,} records → {soil_path}")
    print(f"   💧 Water quality:   {len(water_df):,} records → {water_path}")
    print(f"   🌤️ Weather data:    {len(weather_df):,} records → {weather_path}")
    print(f"   🌾 Crop database:   {len(crop_df):,} records → {crop_path}")
    print(f"\n   Total: {len(soil_df) + len(water_df) + len(weather_df) + len(crop_df):,} records")


if __name__ == "__main__":
    main()
