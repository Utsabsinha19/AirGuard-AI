"""
Integration Tests for AirGuard AI FastAPI Endpoints (FR-3, FR-5, FR-6)
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
async def test_devices_and_ingestion():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # List devices (should auto-seed default multi-room devices)
        res_dev = await ac.get("/api/devices")
        assert res_dev.status_code == 200
        devices = res_dev.json()
        assert len(devices) >= 4

        # Ingest telemetry for AG-001
        payload = {
            "device_id": "AG-001",
            "pm2_5": 14.5,
            "pm10": 20.0,
            "co2": 620.0,
            "voc": 110.0,
            "temperature": 22.5,
            "humidity": 45.0
        }
        res_ingest = await ac.post("/api/telemetry/ingest", json=payload)
        assert res_ingest.status_code == 200
        data = res_ingest.json()
        assert data["device_id"] == "AG-001"
        assert "aqi" in data
        assert "calibrated_pm2_5" in data

        # Check latest telemetry
        res_latest = await ac.get("/api/telemetry/latest/AG-001")
        assert res_latest.status_code == 200
        assert res_latest.json()["pm2_5"] == 14.5


@pytest.mark.asyncio
async def test_predictions_endpoint():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/predictions/AG-001")
        assert res.status_code == 200
        data = res.json()
        assert data["device_id"] == "AG-001"
        assert len(data["predictions"]) == 4
        assert data["predictions"][0]["horizon_mins"] == 15
        assert data["predictions"][2]["horizon_mins"] == 60


@pytest.mark.asyncio
async def test_anomalies_and_simulator_triggers():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Trigger Cooking Smoke scenario
        trigger_resp = await ac.post("/api/simulator/trigger", json={
            "scenario": "COOKING_SMOKE",
            "device_id": "AG-003"
        })
        assert trigger_resp.status_code == 200

        # Diagnosis for AG-003
        diag_resp = await ac.get("/api/anomalies/diagnose/AG-003")
        assert diag_resp.status_code == 200
        diag = diag_resp.json()
        assert diag["root_cause_code"] == "COOKING_SMOKE"


@pytest.mark.asyncio
async def test_actions_tracker():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Log remediation action
        action_payload = {
            "device_id": "AG-001",
            "action_type": "OPEN_WINDOW",
            "description": "Opened master bedroom window for cross ventilation"
        }
        res = await ac.post("/api/actions/log", json=action_payload)
        assert res.status_code == 200
        act = res.json()
        assert act["is_active"] is True
        action_id = act["id"]

        # Check active action
        res_active = await ac.get("/api/actions/active/AG-001")
        assert res_active.status_code == 200
        assert res_active.json()["id"] == action_id

        # Resolve action
        res_resolve = await ac.post(f"/api/actions/{action_id}/resolve")
        assert res_resolve.status_code == 200
        assert res_resolve.json()["is_active"] is False
