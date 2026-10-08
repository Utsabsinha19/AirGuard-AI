"""
Unit Tests for Multi-Sensor Cross-Correlation Anomaly Engine (FR-4.3)
"""

import pytest
from backend.app.ml.anomaly_engine import anomaly_engine


def test_cooking_smoke_diagnosis():
    # Simultaneous spike in PM2.5 and VOC
    reading = {
        "pm2_5": 72.0,
        "co2": 680.0,
        "voc": 520.0,
        "temperature": 24.0,
        "humidity": 55.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is True
    assert diag["root_cause_code"] == "COOKING_SMOKE"
    assert "Culinary" in diag["root_cause_title"] or "Cooking" in diag["root_cause_title"]
    assert "hood" in diag["recommendation"].lower() or "kitchen" in diag["recommendation"].lower()


def test_poor_ventilation_diagnosis():
    # High CO2 and VOC, normal PM2.5
    reading = {
        "pm2_5": 8.0,
        "co2": 1650.0,
        "voc": 360.0,
        "temperature": 23.5,
        "humidity": 52.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is True
    assert diag["root_cause_code"] == "POOR_VENTILATION_OCCUPANCY"
    assert "ventilation" in diag["recommendation"].lower() or "windows" in diag["recommendation"].lower()


def test_chemical_cleaner_diagnosis():
    # Isolated VOC spike
    reading = {
        "pm2_5": 7.0,
        "co2": 510.0,
        "voc": 680.0,
        "temperature": 22.0,
        "humidity": 45.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is True
    assert diag["root_cause_code"] == "CHEMICAL_SOLVENT_EVAPORATION"


def test_clean_baseline():
    reading = {
        "pm2_5": 6.0,
        "co2": 480.0,
        "voc": 80.0,
        "temperature": 21.8,
        "humidity": 45.0
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(reading)
    assert diag["is_anomaly"] is False
    assert diag["severity"] == "NORMAL"
    assert diag["root_cause_code"] == "CLEAN_STABLE"
