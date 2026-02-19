/**
 * AgriSense AI — Data Loader
 * ===========================
 * Generates realistic demo data for dashboard visualization.
 * In production, this would fetch from the ML pipeline's exported JSON.
 */

const AgriData = {
    // ── Soil Health Data ────────────────────────────────────────
    soilHealth: {
        avgScore: 72.4,
        zones: [
            { zone_id: "Zone_1", predicted_score: 78.2, nitrogen_mg_kg: 82, phosphorus_mg_kg: 48, potassium_mg_kg: 65, ph: 6.5, organic_matter_pct: 4.2, moisture_pct: 34, category: "Good", soil_type: "Loamy" },
            { zone_id: "Zone_2", predicted_score: 65.8, nitrogen_mg_kg: 58, phosphorus_mg_kg: 32, potassium_mg_kg: 45, ph: 7.3, organic_matter_pct: 3.1, moisture_pct: 44, category: "Good", soil_type: "Clay" },
            { zone_id: "Zone_3", predicted_score: 48.3, nitrogen_mg_kg: 35, phosphorus_mg_kg: 18, potassium_mg_kg: 28, ph: 5.6, organic_matter_pct: 2.2, moisture_pct: 14, category: "Fair", soil_type: "Sandy" },
            { zone_id: "Zone_4", predicted_score: 74.5, nitrogen_mg_kg: 72, phosphorus_mg_kg: 42, potassium_mg_kg: 58, ph: 6.8, organic_matter_pct: 3.8, moisture_pct: 39, category: "Good", soil_type: "Silt" },
            { zone_id: "Zone_5", predicted_score: 81.2, nitrogen_mg_kg: 95, phosphorus_mg_kg: 52, potassium_mg_kg: 68, ph: 6.3, organic_matter_pct: 4.8, moisture_pct: 31, category: "Excellent", soil_type: "Loamy" },
            { zone_id: "Zone_6", predicted_score: 62.1, nitrogen_mg_kg: 52, phosphorus_mg_kg: 28, potassium_mg_kg: 42, ph: 7.1, organic_matter_pct: 2.8, moisture_pct: 41, category: "Good", soil_type: "Clay Loam" },
            { zone_id: "Zone_7", predicted_score: 55.7, nitrogen_mg_kg: 45, phosphorus_mg_kg: 22, potassium_mg_kg: 35, ph: 5.9, organic_matter_pct: 2.5, moisture_pct: 20, category: "Fair", soil_type: "Sandy Loam" },
            { zone_id: "Zone_8", predicted_score: 85.6, nitrogen_mg_kg: 105, phosphorus_mg_kg: 58, potassium_mg_kg: 78, ph: 5.5, organic_matter_pct: 6.2, moisture_pct: 54, category: "Excellent", soil_type: "Peaty" },
        ],
        categoryDistribution: { "Excellent": 2, "Good": 4, "Fair": 2, "Poor": 0 },
    },

    // ── Nutrient Deficiency Data ────────────────────────────────
    nutrientDeficiency: {
        overallRates: {
            "N_deficient": 28.5,
            "P_deficient": 35.2,
            "K_deficient": 22.8,
            "pH_imbalanced": 18.4,
        },
        recommendations: [
            { type: "critical", nutrient: "Phosphorus", zone: "Zone_3", message: "Critical P deficiency (18 mg/kg). Apply DAP at 60-80 kg/ha before sowing." },
            { type: "warning", nutrient: "Nitrogen", zone: "Zone_3", message: "Low N levels (35 mg/kg). Apply Neem-coated Urea at 80 kg/ha split application." },
            { type: "warning", nutrient: "pH", zone: "Zone_8", message: "Acidic soil (pH 5.5). Apply agricultural lime at 2-3 tons/ha." },
            { type: "info", nutrient: "Potassium", zone: "Zone_3", message: "Moderate K deficiency. Apply MOP at 40 kg/ha as basal dose." },
            { type: "success", nutrient: "NPK Balance", zone: "Zone_5", message: "Excellent nutrient balance. Maintain current fertilization program." },
            { type: "success", nutrient: "Organic Matter", zone: "Zone_8", message: "High organic matter (6.2%). Ideal for most crops." },
        ],
    },

    // ── Water Quality Data ──────────────────────────────────────
    waterQuality: {
        overallGrades: { "A": 1850, "B": 4200, "C": 2800, "D": 900, "F": 250 },
        sources: {
            "Borewell": { grade: "B", ph: 7.5, tds: 602, turbidity: 2.1, do2: 5.2, gradeDistribution: { A: 400, B: 1800, C: 800, D: 300, F: 50 } },
            "River": { grade: "B", ph: 7.0, tds: 348, turbidity: 14.8, do2: 7.1, gradeDistribution: { A: 500, B: 1200, C: 600, D: 150, F: 50 } },
            "Canal": { grade: "C", ph: 7.2, tds: 455, turbidity: 20.2, do2: 5.9, gradeDistribution: { A: 350, B: 800, C: 1000, D: 350, F: 100 } },
            "Rainwater": { grade: "A", ph: 6.5, tds: 48, turbidity: 2.8, do2: 8.1, gradeDistribution: { A: 600, B: 400, C: 400, D: 100, F: 50 } },
        },
    },

    // ── Irrigation Data ─────────────────────────────────────────
    irrigation: {
        waterSavings: 34,
        avgDailyNeed: 8.2,
        droughtRiskZones: ["Zone_3", "Zone_7"],
        zoneSchedule: {
            "Zone_1": { crop: "Rice", soil_type: "Loamy", avg_moisture: 34, avg_need_mm: 8.5, priority: "Medium", recommended_frequency: "Every 2 days" },
            "Zone_2": { crop: "Wheat", soil_type: "Clay", avg_moisture: 44, avg_need_mm: 4.2, priority: "Low", recommended_frequency: "Every 3-4 days" },
            "Zone_3": { crop: "Maize", soil_type: "Sandy", avg_moisture: 14, avg_need_mm: 18.5, priority: "High", recommended_frequency: "Daily" },
            "Zone_4": { crop: "Soybean", soil_type: "Silt", avg_moisture: 39, avg_need_mm: 6.8, priority: "Medium", recommended_frequency: "Every 2 days" },
            "Zone_5": { crop: "Cotton", soil_type: "Loamy", avg_moisture: 31, avg_need_mm: 9.2, priority: "Medium", recommended_frequency: "Every 2 days" },
            "Zone_6": { crop: "Sugarcane", soil_type: "Clay Loam", avg_moisture: 41, avg_need_mm: 5.1, priority: "Low", recommended_frequency: "Every 3-4 days" },
            "Zone_7": { crop: "Potato", soil_type: "Sandy Loam", avg_moisture: 20, avg_need_mm: 15.3, priority: "High", recommended_frequency: "Daily" },
            "Zone_8": { crop: "Tomato", soil_type: "Peaty", avg_moisture: 54, avg_need_mm: 3.5, priority: "Low", recommended_frequency: "Every 3-4 days" },
        },
        weeklyForecast: [
            { week: "W1", need: 7.2 }, { week: "W2", need: 8.5 }, { week: "W3", need: 9.8 },
            { week: "W4", need: 11.2 }, { week: "W5", need: 10.5 }, { week: "W6", need: 8.8 },
            { week: "W7", need: 7.5 }, { week: "W8", need: 6.2 }, { week: "W9", need: 5.8 },
            { week: "W10", need: 7.1 }, { week: "W11", need: 8.4 }, { week: "W12", need: 9.2 },
        ],
    },

    // ── Crop Intelligence Data ──────────────────────────────────
    cropIntelligence: {
        topCrops: { "Rice": 2800, "Wheat": 2200, "Sugarcane": 1500, "Maize": 1200, "Cotton": 1000, "Potato": 800, "Tomato": 600, "Soybean": 500 },
        zoneYields: {
            "Zone_1": { crop: "Rice", predicted_yield: 4.2, expected_baseline: 4.5, yield_efficiency: 93.3, health_score: 78.2 },
            "Zone_2": { crop: "Wheat", predicted_yield: 2.8, expected_baseline: 3.5, yield_efficiency: 80.0, health_score: 65.8 },
            "Zone_3": { crop: "Maize", predicted_yield: 2.5, expected_baseline: 5.0, yield_efficiency: 50.0, health_score: 48.3 },
            "Zone_4": { crop: "Soybean", predicted_yield: 2.2, expected_baseline: 2.5, yield_efficiency: 88.0, health_score: 74.5 },
            "Zone_5": { crop: "Cotton", predicted_yield: 1.9, expected_baseline: 2.0, yield_efficiency: 95.0, health_score: 81.2 },
            "Zone_6": { crop: "Sugarcane", predicted_yield: 58.0, expected_baseline: 70.0, yield_efficiency: 82.9, health_score: 62.1 },
            "Zone_7": { crop: "Potato", predicted_yield: 14.0, expected_baseline: 25.0, yield_efficiency: 56.0, health_score: 55.7 },
            "Zone_8": { crop: "Tomato", predicted_yield: 28.0, expected_baseline: 30.0, yield_efficiency: 93.3, health_score: 85.6 },
        },
        zoneCropRecommendations: {
            "Zone_1": [{ crop: "Rice", confidence: 89.2, yield: 4.5 }, { crop: "Sugarcane", confidence: 72.1, yield: 70.0 }, { crop: "Banana", confidence: 68.5, yield: 40.0 }],
            "Zone_2": [{ crop: "Wheat", confidence: 85.4, yield: 3.5 }, { crop: "Barley", confidence: 71.2, yield: 3.0 }, { crop: "Mustard", confidence: 65.8, yield: 1.8 }],
            "Zone_3": [{ crop: "Millet", confidence: 78.3, yield: 1.5 }, { crop: "Groundnut", confidence: 72.1, yield: 2.0 }, { crop: "Sesame", confidence: 65.0, yield: 0.8 }],
            "Zone_4": [{ crop: "Soybean", confidence: 91.2, yield: 2.5 }, { crop: "Chickpea", confidence: 78.4, yield: 1.5 }, { crop: "Lentil", confidence: 72.3, yield: 1.2 }],
            "Zone_5": [{ crop: "Cotton", confidence: 88.5, yield: 2.0 }, { crop: "Sunflower", confidence: 75.3, yield: 2.0 }, { crop: "Maize", confidence: 71.8, yield: 5.0 }],
            "Zone_6": [{ crop: "Sugarcane", confidence: 92.1, yield: 70.0 }, { crop: "Rice", confidence: 78.5, yield: 4.5 }, { crop: "Turmeric", confidence: 72.0, yield: 8.0 }],
            "Zone_7": [{ crop: "Potato", confidence: 76.8, yield: 25.0 }, { crop: "Carrot", confidence: 71.2, yield: 25.0 }, { crop: "Onion", confidence: 68.5, yield: 20.0 }],
            "Zone_8": [{ crop: "Tomato", confidence: 90.5, yield: 30.0 }, { crop: "Ginger", confidence: 82.3, yield: 5.0 }, { crop: "Turmeric", confidence: 78.1, yield: 8.0 }],
        },
    },

    // ── Alerts Data ─────────────────────────────────────────────
    alerts: [
        { type: "critical", icon: "🔴", title: "Severe Moisture Deficit — Zone 3", desc: "Soil moisture at 14% (critical: <20%). Immediate irrigation required for Maize crop survival.", time: "5 min ago" },
        { type: "critical", icon: "🔴", title: "Low Yield Forecast — Zone 3", desc: "Predicted yield only 50% of potential due to poor soil health (48.3/100). Urgent intervention needed.", time: "12 min ago" },
        { type: "warning", icon: "🟡", title: "Phosphorus Deficiency — Zone 3", desc: "P levels at 18 mg/kg (critical threshold: 25). Apply DAP 60-80 kg/ha before next sowing.", time: "25 min ago" },
        { type: "warning", icon: "🟡", title: "High Irrigation Demand — Zone 7", desc: "Sandy loam soil requires daily watering. Average need: 15.3mm/day. Consider drip irrigation.", time: "1 hr ago" },
        { type: "warning", icon: "🟡", title: "Acidic Soil Alert — Zone 8", desc: "pH at 5.5. Below optimal range (6.0-7.5). Lime application recommended at 2-3 tons/ha.", time: "2 hrs ago" },
        { type: "info", icon: "🔵", title: "Water Savings Report", desc: "Smart irrigation saving 34% water compared to uniform irrigation across all zones.", time: "3 hrs ago" },
        { type: "info", icon: "🔵", title: "Excellent Health — Zone 5", desc: "Soil health score 81.2/100 (Excellent). Current management practices are optimal.", time: "4 hrs ago" },
        { type: "info", icon: "🔵", title: "Crop Recommendation Update", desc: "Updated crop recommendations based on latest soil and weather data for all 8 zones.", time: "5 hrs ago" },
        { type: "info", icon: "🔵", title: "Weather Forecast", desc: "Clear skies expected for next 5 days. Temp: 28-32°C. No rainfall expected — plan irrigation accordingly.", time: "6 hrs ago" },
    ],

    // ── Weather Data ────────────────────────────────────────────
    weather: {
        current: { temp: 28, humidity: 65, condition: "Clear", wind: 12, rainfall_today: 0, uv: 7 },
    },
};
