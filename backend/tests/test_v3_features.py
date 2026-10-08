"""
Unit and integration tests for AirGuard AI Version 3.0:
- Next-Gen Multi-Sensor Anomaly Root Causes (Material Off-Gassing, Wildfire Smoke, HVAC Filter Saturation)
- ST-GNN Spatio-Temporal Graph Cross-Room Diffusion
- Closed-Loop Smart Home Actuation (Matter / Home Assistant)
- Personal Cumulative Inhalation Dosage & Clinical Vulnerability Profiling
- Enterprise Spatial Hierarchy
- Fleet Federated Cross-Calibration
"""

import pytest
import numpy as np
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database import init_db
from backend.app.ml.anomaly_engine import anomaly_engine
from backend.app.ml.st_gnn import st_gnn
from backend.app.actuation.engine import actuation_engine
from backend.app.health.exposure_engine import exposure_engine


# ==========================================
# 1. v3.0 Anomaly Diagnostics Tests
# ==========================================
def test_material_off_gassing_diagnosis():
    """Verify HCHO spike triggers MATERIAL_OFF_GASSING diagnosis."""
    features = {
        "pm2_5": 8.0,
        "co2": 520.0,
        "voc": 380.0,
        "hcho": 0.125,         # Severe formaldehyde
        "voc_index": 350,
        "nox_index": 1,
        "temperature": 23.5,
        "humidity": 45.0,
        "pressure": 1013.25
    }
    history = [
        {"pm2_5": 7.5, "co2": 500.0, "voc": 80.0, "hcho": 0.02, "temperature": 23.0, "humidity": 44.0}
        for _ in range(15)
    ]

    res = anomaly_engine.detect_anomalies_and_diagnose(features, history)
    assert res["is_anomaly"] is True
    assert res["root_cause_code"] == "MATERIAL_OFF_GASSING"
    assert "HCHO" in res["sensor_contributions"]
    assert "Formaldehyde" in res["description"]


def test_wildfire_smoke_diagnosis():
    """Verify sub-micron particulate surge with barometric shift triggers WILDFIRE_SMOKE_INFILTRATION."""
    features = {
        "pm2_5": 115.0,
        "pm10": 140.0,
        "pm0_3": 52.0,
        "co2": 580.0,
        "voc": 220.0,
        "hcho": 0.02,
        "voc_index": 180,
        "nox_index": 3,
        "temperature": 24.0,
        "humidity": 35.0,
        "pressure": 1002.5       # Barometric inversion
    }
    history = [
        {"pm2_5": 12.0, "co2": 550.0, "voc": 90.0, "temperature": 22.0, "humidity": 45.0}
        for _ in range(15)
    ]

    res = anomaly_engine.detect_anomalies_and_diagnose(features, history)
    assert res["is_anomaly"] is True
    assert res["root_cause_code"] == "WILDFIRE_SMOKE_INFILTRATION"
    assert res["severity"] == "CRITICAL"


# ==========================================
# 2. ST-GNN Spatio-Temporal Diffusion Tests
# ==========================================
def test_st_gnn_diffusion_model():
    """Test ST-GNN graph laplacian forward diffusion projections."""
    room_metrics = {
        "Kitchen": 65.0,
        "Living Room": 15.0,
        "Bedroom": 12.0,
        "Office": 10.0,
        "Nursery": 8.0,
        "Outdoor": 22.0
    }

    res = st_gnn.predict_diffusion(room_metrics)
    assert "nodes" in res
    assert "edges" in res
    assert len(res["nodes"]) == len(room_metrics)
    
    # Kitchen has high concentration, should have outward diffusion vectors
    node_kitchen = next(n for n in res["nodes"] if n["room_name"] == "Kitchen")
    assert node_kitchen["predicted_pm2_5_60m"] < node_kitchen["current_pm2_5"]


@pytest.mark.asyncio
async def test_st_gnn_endpoint():
    """Test GET /api/predictions/diffusion/cross-room returns valid graph schema."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/predictions/diffusion/cross-room")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) >= 3


# ==========================================
# 3. Smart Actuation Engine Tests
# ==========================================
@pytest.mark.asyncio
async def test_actuation_api_endpoints():
    """Test actuator listing, manual control, and log retrieval."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # List actuators
        r_list = await ac.get("/api/actuation/devices")
        assert r_list.status_code == 200
        devices = r_list.json()
        assert len(devices) > 0

        target_id = devices[0]["id"]

        # Dispatch control command
        r_ctrl = await ac.post("/api/actuation/control", json={
            "actuator_id": target_id,
            "fan_speed": "BOOST",
            "state": "ON"
        })
        assert r_ctrl.status_code == 200
        res_dev = r_ctrl.json()
        assert res_dev["fan_speed"] == "BOOST"
        assert res_dev["state"] == "ON"

        # Retrieve actuation logs
        r_logs = await ac.get(f"/api/actuation/logs?actuator_id={target_id}&limit=5")
        assert r_logs.status_code == 200
        logs = r_logs.json()
        assert len(logs) > 0


# ==========================================
# 4. Personal Health Exposure Tests
# ==========================================
@pytest.mark.asyncio
async def test_health_api_endpoints():
    """Test profile updates and real-time exposure retrieval."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Update profile
        r_up = await ac.post("/api/health/profile", json={
            "user_id": "test_athlete_01",
            "profile_type": "CARDIOVASCULAR"
        })
        assert r_up.status_code == 200
        prof = r_up.json()
        assert prof["profile_type"] == "CARDIOVASCULAR"

        # Fetch exposure metrics
        r_exp = await ac.get("/api/health/exposure?user_id=test_athlete_01&window_hours=24")
        assert r_exp.status_code == 200
        exp = r_exp.json()
        assert exp["profile_type"] == "CARDIOVASCULAR"
        assert "cumulative_intake_pm25_ug" in exp
        assert "health_risk_score" in exp


# ==========================================
# 5. Enterprise Hierarchy & Federated Calibration Tests
# ==========================================
@pytest.mark.asyncio
async def test_enterprise_hierarchy_endpoint():
    """Test enterprise 7-level spatial hierarchy API."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/enterprise/hierarchy")
        assert resp.status_code == 200
        data = resp.json()
        assert "organization" in data
        assert "campuses" in data["organization"]
        assert len(data["organization"]["campuses"]) > 0
        campus = data["organization"]["campuses"][0]
        assert "buildings" in campus
        building = campus["buildings"][0]
        assert "floors" in building


@pytest.mark.asyncio
async def test_fleet_federated_calibration():
    """Test zero-point baseline sync across device fleet."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/devices/AG-001/federated-calibrate")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "zero_point_reference_pm2_5" in data
        assert "sync_timestamp" in data
