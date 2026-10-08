"""
Integration Tests for AirGuard AI FastAPI Endpoints (Enhanced, Section 2.1, 2.2, 2.3)
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database import init_db


@pytest.mark.asyncio
async def test_health_and_root():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_devices_and_calibration():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Check floorplan coordinates in device listing
        res_dev = await ac.get("/api/devices")
        assert res_dev.status_code == 200
        devices = res_dev.json()
        assert len(devices) >= 4
        assert "x_coord" in devices[0]
        assert "latitude" in devices[0]

        # Test device calibration endpoint (Section 2.2)
        cal_payload = {
            "pm_zero_offset": 1.5,
            "pm_gain": 0.95,
            "voc_zero_offset": 5.0,
            "voc_gain": 1.05
        }
        res_cal = await ac.post("/api/devices/AG-001/calibrate", json=cal_payload)
        assert res_cal.status_code == 200
        data = res_cal.json()
        assert data["pm_zero_offset"] == 1.5
        assert data["pm_gain"] == 0.95


@pytest.mark.asyncio
async def test_ingestion_and_csv_export():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Ingest telemetry with expanded metrics
        payload = {
            "device_id": "AG-001",
            "pm2_5": 16.0,
            "pm10": 22.0,
            "co2": 650.0,
            "voc": 115.0,
            "temperature": 22.5,
            "humidity": 45.0,
            "pressure": 1012.4,
            "ambient_light": 230.0,
            "noise_level": 44.0,
            "battery_pct": 92
        }
        res_ingest = await ac.post("/api/telemetry/ingest", json=payload)
        assert res_ingest.status_code == 200
        data = res_ingest.json()
        assert data["pressure"] == 1012.4
        assert data["ambient_light"] == 230.0

        # Export CSV (Section 2.1)
        res_export = await ac.get("/api/telemetry/export/AG-001")
        assert res_export.status_code == 200
        assert "text/csv" in res_export.headers["content-type"]
        assert "timestamp,device_id" in res_export.text


@pytest.mark.asyncio
async def test_multi_model_comparison_endpoint():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test specific architectures: gbm, lstm, gru, tcn
        for model in ["baseline", "lstm", "gru", "tcn"]:
            res = await ac.get(f"/api/predictions/AG-001?model_type={model}")
            assert res.status_code == 200
            assert len(res.json()["predictions"]) == 4

        # Test multi-model comparison route
        res_comp = await ac.get("/api/predictions/compare/AG-001")
        assert res_comp.status_code == 200
        comp_data = res_comp.json()
        assert len(comp_data["models"]) == 4
        model_names = [m["model"] for m in comp_data["models"]]
        assert "Gradient Boosting (GBM)" in model_names
        assert "PyTorch LSTM" in model_names
        assert "PyTorch GRU" in model_names
        assert "Temporal CNN (TCN)" in model_names


@pytest.mark.asyncio
async def test_alert_to_action_workflow():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Trigger an anomaly to ensure an alert exists
        await ac.post("/api/simulator/trigger", json={
            "scenario": "COOKING_SMOKE",
            "device_id": "AG-003"
        })

        # Fetch alerts
        alerts_res = await ac.get("/api/alerts")
        alerts = alerts_res.json()
        assert len(alerts) > 0
        alert_id = alerts[0]["id"]

        # Convert alert to active remediation action
        conv_res = await ac.post(f"/api/alerts/{alert_id}/convert-to-action")
        assert conv_res.status_code == 200
        action_data = conv_res.json()
        assert action_data["is_active"] is True
        assert action_data["device_id"] == alerts[0]["device_id"]


@pytest.mark.asyncio
async def test_nested_v2_telemetry_and_batch_flush():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Ingest using Section 3.1 nested metrics schema
        v2_payload = {
            "device_id": "AG-001",
            "location": "Master Bedroom",
            "timestamp": "2026-10-08T02:45:00Z",
            "metrics": {
                "pm2_5": 34.2,
                "pm10": 48.1,
                "co2": 1180.0,
                "voc": 320.0,
                "temperature": 27.4,
                "humidity": 64.0,
                "pressure": 1012.5,
                "battery_pct": 88
            }
        }
        res_ingest = await ac.post("/api/telemetry/ingest", json=v2_payload)
        assert res_ingest.status_code == 200
        data = res_ingest.json()
        assert data["pm2_5"] == 34.2
        assert data["co2"] == 1180.0
        assert data["pressure"] == 1012.5

        # Test throttled batch flush endpoint (Section 1.2, 3.2)
        batch = [
            {
                "device_id": "AG-002",
                "metrics": {"pm2_5": 12.0, "co2": 520.0, "voc": 80.0, "temperature": 21.0, "humidity": 44.0}
            },
            {
                "device_id": "AG-002",
                "metrics": {"pm2_5": 14.0, "co2": 540.0, "voc": 85.0, "temperature": 21.2, "humidity": 44.5}
            }
        ]
        res_batch = await ac.post("/api/telemetry/batch", json=batch)
        assert res_batch.status_code == 200
        batch_res = res_batch.json()
        assert len(batch_res) == 2


@pytest.mark.asyncio
async def test_device_zone_topology_and_decay_rates():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Check zone in devices
        res_dev = await ac.get("/api/devices")
        assert res_dev.status_code == 200
        devices = res_dev.json()
        zones = [d.get("zone") for d in devices]
        assert "Bedroom" in zones or "Living Room" in zones

        # Update zone topology (Section 4.1)
        up_res = await ac.put("/api/devices/AG-001", json={"zone": "Master Suite", "room": "Master Bedroom v2"})
        assert up_res.status_code == 200
        assert up_res.json()["zone"] == "Master Suite"

        # Log remediation and verify real-time decay rate calculations (Section 4.2)
        log_res = await ac.post("/api/actions/log", json={
            "device_id": "AG-001",
            "action_type": "OPEN_WINDOW",
            "description": "Opened bedroom window"
        })
        assert log_res.status_code == 200
        action_id = log_res.json()["id"]

        # Ingest new reading with reduced CO2 to trigger decay calculation
        await ac.post("/api/telemetry/ingest", json={
            "device_id": "AG-001",
            "metrics": {"pm2_5": 8.0, "co2": 650.0, "voc": 80.0, "temperature": 21.0, "humidity": 42.0}
        })

        # Resolve action
        res_action = await ac.post(f"/api/actions/{action_id}/resolve")
        assert res_action.status_code == 200
        resolved_data = res_action.json()
        assert resolved_data["is_active"] is False
        assert "recovery_message" in resolved_data or "decay_rate" in resolved_data

