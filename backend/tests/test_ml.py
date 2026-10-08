"""
Unit & Integration Tests for ML Models and Calibration Logic (FR-4, NFR-3)
"""

import pytest
from backend.app.ml.calibration import (
    calibrate_pm25,
    calibrate_voc,
    compute_comprehensive_aqi,
    calculate_absolute_humidity
)
from backend.app.ml.predictor_baseline import baseline_predictor
from backend.app.ml.predictor_neural import neural_predictor


def test_pm25_hygroscopic_calibration():
    # At low humidity (<50%), minimal correction
    cal_dry = calibrate_pm25(20.0, 35.0)
    assert cal_dry == 20.0

    # At high humidity (85%), optical hygroscopic growth should be corrected downward
    cal_humid = calibrate_pm25(50.0, 85.0)
    assert cal_humid < 50.0
    assert cal_humid > 25.0


def test_voc_temperature_humidity_compensation():
    # Target condition: 25C, 50% RH
    val = calibrate_voc(150.0, 25.0, 50.0)
    assert abs(val - 150.0) < 5.0

    # Test extreme temperature/humidity variation
    val_cold = calibrate_voc(200.0, 16.0, 30.0)
    assert val_cold > 0.0


def test_epa_aqi_computation():
    # Good AQI (low PM2.5)
    res_good = compute_comprehensive_aqi(pm25=8.0, co2=500.0, voc=90.0)
    assert res_good["aqi"] <= 50
    assert res_good["category"] == "Good"

    # Moderate AQI
    res_mod = compute_comprehensive_aqi(pm25=22.0, co2=600.0, voc=120.0)
    assert 51 <= res_mod["aqi"] <= 100
    assert res_mod["category"] == "Moderate"

    # Unhealthy (elevated PM2.5)
    res_unhealthy = compute_comprehensive_aqi(pm25=75.0, co2=800.0, voc=250.0)
    assert res_unhealthy["aqi"] >= 151
    assert res_unhealthy["dominant_pollutant"] == "PM2.5"


def test_multi_horizon_forecasting():
    # Test +15m, +30m, +1h, and +6h forecast outputs
    current = {
        "pm2_5": 25.0,
        "co2": 850.0,
        "voc": 180.0,
        "temperature": 23.0,
        "humidity": 50.0
    }
    preds = baseline_predictor.predict_horizons(current)
    assert len(preds) == 4
    horizons = [p["horizon_mins"] for p in preds]
    assert horizons == [15, 30, 60, 360]

    for p in preds:
        assert p["predicted_pm2_5"] >= 0.0
        assert p["predicted_co2"] >= 350.0
        assert p["confidence_lower"] <= p["predicted_pm2_5"] <= p["confidence_upper"]
        assert "aqi_category" in p


def test_device_offset_and_gain_calibration():
    # Test zero offset subtraction and gain factor scaling
    raw_pm = 25.0
    zero_offset = 5.0
    gain = 1.2
    # At 40% RH (no hygroscopic effect): (25 - 5) * 1.2 = 24.0
    cal_pm = calibrate_pm25(raw_pm, humidity_rh=40.0, zero_offset=zero_offset, gain_scale=gain)
    assert abs(cal_pm - 24.0) < 0.1

    raw_voc = 200.0
    cal_voc = calibrate_voc(raw_voc, temp_c=25.0, humidity_rh=50.0, zero_offset=20.0, gain_scale=0.9)
    # (200 - 20) * 0.9 = 162.0 (approx due to AH)
    assert abs(cal_voc - 162.0) < 5.0


def test_neural_sequence_predictors():
    # Test PyTorch LSTM, GRU, and TCN models
    history = [
        {"pm2_5": 15.0 + i, "co2": 600.0, "voc": 120.0, "temperature": 22.0, "humidity": 45.0}
        for i in range(12)
    ]
    for model_type in ["lstm", "gru", "tcn"]:
        preds = neural_predictor.predict_sequence(history, architecture=model_type)
        assert len(preds) == 4
        for p in preds:
            assert p["predicted_pm2_5"] >= 0.0
            assert p["predicted_co2"] >= 300.0
            assert p["confidence_lower"] <= p["predicted_pm2_5"] <= p["confidence_upper"]


def test_model_comparison_benchmark_metadata():
    comparison = neural_predictor.get_model_comparison()
    assert len(comparison) == 4
    names = [c["model"] for c in comparison]
    assert "Gradient Boosting (GBM)" in names
    assert "PyTorch LSTM" in names
    assert "PyTorch GRU" in names
    assert "Temporal CNN (TCN)" in names
    for m in comparison:
        assert m["mae_1h"] > 0
        assert m["r2_1h"] > 0
        assert "latency_ms" in m

