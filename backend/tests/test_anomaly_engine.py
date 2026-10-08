"""
Unit Tests for Context-Aware Multi-Sensor Anomaly Engine (FR-4.3, Section 2.2)
"""

import pytest
from backend.app.ml.anomaly_engine import anomaly_engine


def test_cooking_smoke_diagnosis():
    reading = {
        "pm2_5": 72.0, "co2": 680.0, "voc": 520.0,
        "temperature": 24.0, "humidity": 55.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is True
    assert diag["root_cause_code"] == "COOKING_SMOKE"


def test_poor_ventilation_diagnosis():
    reading = {
        "pm2_5": 8.0, "co2": 1650.0, "voc": 360.0,
        "temperature": 23.5, "humidity": 52.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is True
    assert diag["root_cause_code"] == "POOR_VENTILATION_OCCUPANCY"


def test_chemical_cleaner_diagnosis():
    reading = {
        "pm2_5": 7.0, "co2": 510.0, "voc": 680.0,
        "temperature": 22.0, "humidity": 45.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is True
    assert diag["root_cause_code"] == "CHEMICAL_SOLVENT_EVAPORATION"


def test_high_occupancy_activity_diagnosis():
    # Context-aware: High acoustic noise + High CO2 + High VOC
    reading = {
        "pm2_5": 14.0, "co2": 1550.0, "voc": 380.0,
        "noise_level": 74.0, "temperature": 24.0, "humidity": 55.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is True
    assert diag["root_cause_code"] == "HIGH_OCCUPANCY_ACTIVITY"


def test_weather_inversion_smog_diagnosis():
    # Context-aware: Falling pressure + High PM2.5, normal VOC
    reading = {
        "pm2_5": 48.0, "co2": 550.0, "voc": 110.0,
        "pressure": 1002.5, "temperature": 18.0, "humidity": 65.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is True
    assert diag["root_cause_code"] == "WEATHER_INVERSION_SMOG"


def test_clean_baseline():
    reading = {
        "pm2_5": 6.0, "co2": 480.0, "voc": 80.0,
        "temperature": 21.8, "humidity": 45.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is False
    assert diag["severity"] == "NORMAL"


def test_hvac_filter_failure_diagnosis():
    # v2.0 Signature: Gradual PM2.5 + PM10 + elevated Humidity with clean VOC & CO2
    reading = {
        "pm2_5": 28.0,
        "pm10": 42.0,
        "co2": 580.0,
        "voc": 95.0,
        "temperature": 22.0,
        "humidity": 65.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is True
    assert diag["root_cause_code"] == "HVAC_FILTER_FAILURE"
    assert "clean air purifier / HVAC filters" in diag["recommendation"]

