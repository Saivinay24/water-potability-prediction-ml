# AgriSense AI — Sensor Integration Guide

## Overview

This guide explains how to connect real IoT sensors to AgriSense AI, replacing the synthetic data generator with live farm readings.

## Supported Sensor Types

### Soil Sensors

| Parameter | Sensor Model | Interface | Range | Accuracy |
|-----------|-------------|-----------|-------|----------|
| **NPK** | JXBS-3001-NPK | RS485/Modbus | N: 0-1999mg/kg | ±2% |
| **pH** | SEN0161-V2 | Analog (0-5V) | 0-14 | ±0.1 |
| **Moisture** | Capacitive v1.2 | Analog | 0-100% | ±3% |
| **Temperature** | DS18B20 | OneWire | -55 to 125°C | ±0.5°C |
| **EC** | SEN0244 | Analog | 0-20 mS/cm | ±5% |

### Water Quality Sensors

| Parameter | Sensor Model | Interface | Range |
|-----------|-------------|-----------|-------|
| **pH** | PH-4502C | Analog | 0-14 |
| **TDS** | TDS Meter v1.0 | Analog | 0-1000 ppm |
| **Turbidity** | SEN0189 | Analog | 0-3000 NTU |
| **Dissolved O₂** | SEN0237-A | Analog | 0-20 mg/L |

### Weather Station

| Parameter | Sensor Model | Interface |
|-----------|-------------|-----------|
| **Temp + Humidity** | DHT22/BME280 | I2C/GPIO |
| **Rainfall** | Tipping Bucket | Digital interrupt |
| **Wind** | Anemometer | Pulse counting |
| **Solar Radiation** | BH1750 + pyranometer | I2C |
| **UV Index** | VEML6075 | I2C |

## Hardware Setup

### Option A: Arduino + LoRaWAN (Recommended for Fields)

```
                 ┌──────────────┐
    Sensor ──────│   Arduino    │
    Sensor ──────│   Mega 2560  │──── LoRa Module (SX1276)
    Sensor ──────│              │           │
                 └──────────────┘           │ LoRa (915MHz)
                                            │
                                   ┌────────▼────────┐
                                   │  LoRa Gateway    │
                                   │  (RPi + RAK2245) │
                                   └────────┬────────┘
                                            │ WiFi/Ethernet
                                   ┌────────▼────────┐
                                   │  AgriSense AI    │
                                   │  (Data Pipeline) │
                                   └─────────────────┘
```

**Why LoRaWAN**: Long range (2-15km), low power, penetrates vegetation. Perfect for farms.

### Option B: Raspberry Pi + WiFi (Small Farms / Greenhouses)

```
    Sensor ──────┐
    Sensor ──────┤ Raspberry Pi 4
    Sensor ──────┤ + ADC (ADS1115)
                 │
                 └── WiFi → AgriSense API
```

## Data Format

Each sensor reading should produce a CSV row or JSON object matching this schema:

### Soil Sensor Reading
```json
{
    "timestamp": "2025-03-15 10:30:00",
    "zone_id": "Zone_1",
    "soil_type": "Loamy",
    "nitrogen_mg_kg": 82.5,
    "phosphorus_mg_kg": 45.2,
    "potassium_mg_kg": 63.8,
    "ph": 6.5,
    "organic_matter_pct": 4.2,
    "moisture_pct": 34.1,
    "soil_temperature_c": 28.3,
    "ec_mscm": 1.8
}
```

### Water Quality Reading
```json
{
    "timestamp": "2025-03-15 10:30:00",
    "source_type": "Borewell",
    "ph": 7.5,
    "tds_ppm": 602.3,
    "turbidity_ntu": 2.1,
    "dissolved_oxygen_mg_l": 5.2,
    "hardness_mg_l": 245.0,
    "chloride_mg_l": 98.5,
    "sulfate_mg_l": 78.2,
    "nitrate_mg_l": 14.8,
    "water_temperature_c": 26.5
}
```

## Communication Protocols

### MQTT (Recommended)

```
Broker: mqtt://your-server:1883
Topics:
  agrisense/soil/{zone_id}     → Soil readings
  agrisense/water/{source_id}  → Water readings
  agrisense/weather             → Weather data

QoS: 1 (at least once delivery)
Payload: JSON format as shown above
Interval: Every 15 minutes (configurable)
```

### HTTP REST

```
POST /api/v1/readings/soil
POST /api/v1/readings/water
POST /api/v1/readings/weather

Content-Type: application/json
Body: Sensor reading JSON
```

### CSV File Drop

Place CSV files matching the column schema into `data/raw/` and re-run the pipeline:
```bash
python scripts/run_pipeline.py
```

## Calibration

### Soil pH Sensor Calibration
1. Prepare pH 4.0 and pH 7.0 buffer solutions
2. Immerse sensor in pH 7.0 buffer → record voltage
3. Immerse sensor in pH 4.0 buffer → record voltage
4. Calculate slope: `pH = (voltage - offset) / slope`

### TDS Sensor Calibration
1. Use 342 ppm NaCl calibration solution
2. Immerse sensor → adjust potentiometer until reading matches

### NPK Sensor (RS485)
1. No user calibration needed — factory calibrated
2. Verify Modbus address (default: 0x01)
3. Baud rate: 9600, 8N1
4. Register map: N=0x001E, P=0x001F, K=0x0020

## Power Considerations

| Setup | Power Source | Battery Life |
|-------|-------------|-------------|
| Arduino + LoRa | Solar panel (6V 3W) + LiPo | Indefinite |
| Raspberry Pi | Solar panel (12V 10W) + battery | Indefinite |
| Arduino + WiFi | Solar panel (6V 3W) + LiPo | Indefinite |
| Wired | 5V USB / PoE | N/A |

**Sleep mode**: Configure sensors to sleep between readings. Wake every 15 minutes for soil, 30 minutes for weather. This extends battery life 10x.
