"""
AirGuard AI - Comprehensive Test Suite for Version 4.0 Grid Features
Tests:
- Physics-Informed Neural Networks (PINN) 3D Fluid Dynamics & Street Canyon
- Generative Atmospheric & Health Copilot ("AirGuard Agent")
- Multi-Sensor Correlation Signatures with Acoustic FFT Spectrum
- Enterprise BMS (BACnet/IP, Modbus TCP, KNX, Sparkplug B)
- Smart Grid Dynamic Tariff Demand Response & Pre-emptive Scrubbing
- ESP-NOW Swarm Mesh Topology & Peer Consensus Drift Correction
- Biometric Wearable Health Fusion & Dynamic VE(HR) Inhalation Intake
- Vector Memory Semantic Incident Retrieval
- Zero-Trust mTLS X.509 Verification & Differential Privacy Laplace Perturbation
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.ml.pinn_engine import pinn_engine
from backend.app.ml.copilot_agent import copilot_agent
from backend.app.actuation.bms_grid_engine import bms_grid_engine
from backend.app.services.vector_memory import vector_memory
from backend.app.services.zero_trust import zero_trust_security
from backend.app.services.mesh_wearable_engine import mesh_wearable_engine
from backend.app.health.exposure_engine import exposure_engine
from backend.app.ml.anomaly_engine import anomaly_engine


@pytest.mark.asyncio
async def test_pinn_3d_indoor_fluid_dynamics():
    sim = pinn_engine.simulate_indoor_3d(
        room_id="ROOM-LIVING-ROOM",
        inlet_velocity_mps=1.5,
        vent_exhaust_rate_cfm=250.0,
        emission_source_ug_s=40.0,
        resolution_x=6,
        resolution_y=6,
        resolution_z=4
    )
    assert sim["domain_type"] == "INDOOR_3D_ROOM"
    assert len(sim["grid_points"]) == 6 * 6 * 4
    assert sim["navier_stokes_residual"] >= 0.0
    assert "optimal_purifier_coordinates" in sim
    assert sim["predicted_clear_time_mins"] > 0.0


@pytest.mark.asyncio
async def test_pinn_street_canyon_dispersion():
    # Test Skimming Flow Regime (H/W >= 0.75)
    canyon = pinn_engine.simulate_street_canyon(
        canyon_id="CANYON-DOWNTOWN-01",
        building_height_m=30.0,
        street_width_m=20.0,
        ambient_wind_mps=4.5,
        traffic_emissions_ug_m_s=85.0
    )
    assert canyon["aspect_ratio"] == 1.5
    assert canyon["recirculation_regime"] == "SKIMMING_FLOW"
    assert canyon["leeward_concentration_ug_m3"] > canyon["windward_concentration_ug_m3"]
    assert canyon["canyon_vortex_rpm"] > 0.0


@pytest.mark.asyncio
async def test_generative_copilot_advisories():
    # 1. Cooking fumes
    adv1 = copilot_agent.generate_advisory("COOKING_SMOKE", pm25=88.0, voc=320.0, room_name="Kitchen")
    assert "Kitchen" in adv1["plain_language_advisory"]
    assert "cooking fumes" in adv1["plain_language_advisory"]

    # 2. Structural off-gassing
    adv2 = copilot_agent.generate_advisory("MATERIAL_OFF_GASSING", hcho=0.12, room_name="Study")
    assert "Formaldehyde" in adv2["plain_language_advisory"]
    assert "Study" in adv2["location"]

    # 3. Wildfire smoke
    adv3 = copilot_agent.generate_advisory("WILDFIRE_SMOKE_INFILTRATION", pm25=110.0, room_name="Office")
    assert "Wildfire" in adv3["plain_language_advisory"]


@pytest.mark.asyncio
async def test_generative_copilot_qa_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/copilot/query", json={
            "query": "What is my air quality right now?",
            "device_id": "AG-001"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "AQI" in data["response"]
        assert len(data["recommended_actions"]) > 0


@pytest.mark.asyncio
async def test_industrial_bms_integration():
    devices = bms_grid_engine.get_all_devices()
    assert len(devices) >= 4
    protocols = [d["protocol"] for d in devices]
    assert "BACNET_IP" in protocols
    assert "MODBUS_TCP" in protocols
    assert "SPARKPLUG_B" in protocols

    # Control a device
    updated = bms_grid_engine.control_device("BACNET-VAV-FLOOR1", target_speed_pct=85, damper_pct=90)
    assert updated["speed_pct"] == 85
    assert updated["damper_pct"] == 90
    assert updated["power_draw_kw"] > 0.0


@pytest.mark.asyncio
async def test_grid_aware_demand_response():
    status = bms_grid_engine.evaluate_grid_demand_response(
        predicted_pm25_spike_mins=20,
        forecasted_pm25_ug_m3=65.0
    )
    assert "current_tariff_tier" in status
    assert "calculated_cadr_cfm" in status
    assert status["calculated_cadr_cfm"] > 0.0
    assert status["cadr_decay_constant_k"] > 0.0


@pytest.mark.asyncio
async def test_esp_now_swarm_mesh_and_consensus():
    topo = mesh_wearable_engine.get_mesh_topology()
    assert topo["total_nodes"] >= 4
    assert topo["healthy_mesh"] is True

    # Peer consensus baseline drift correction
    consensus = mesh_wearable_engine.run_peer_consensus_calibration({
        "NODE-A": 10.0,
        "NODE-B": 14.0,
        "NODE-C": 12.0
    })
    assert consensus["baseline_pm25_median"] == 12.0
    assert consensus["drift_variance_reduction_pct"] > 0.0


@pytest.mark.asyncio
async def test_biometric_wearable_dynamic_ve_intake():
    # Sync wearable
    sync = mesh_wearable_engine.sync_wearable(
        user_id="runner_01",
        source="GARMIN",
        heart_rate_bpm=125.0,
        hrv_ms=45.0,
        spo2_pct=97.0,
        respiratory_rate_bpm=24.0
    )
    assert sync["source"] == "GARMIN"

    # Evaluate dynamic intake
    intake = await exposure_engine.calculate_dynamic_intake(
        user_id="runner_01",
        heart_rate_bpm=125.0
    )
    assert intake["dynamic_ve_lpm"] > 12.0  # Dynamic minute ventilation exceeds resting rate
    assert intake["excess_intake_due_to_hr_pct"] > 50.0
    assert intake["physiological_strain_index"] in ["HIGH_STRAIN", "MILD_STRAIN", "BRONCHIAL_WARNING"]


@pytest.mark.asyncio
async def test_hybrid_vector_database_incident_memory():
    # Query vector memory with a cooking smoke signature
    sig = {
        "pm2_5": 85.0,
        "co2": 610.0,
        "voc": 320.0,
        "hcho": 0.02,
        "acoustic_db": 66.0
    }
    matches = vector_memory.search_similar_incidents(sig, top_k=2)
    assert len(matches) == 2
    assert matches[0]["similarity_score"] > 0.70
    assert "resolution_strategy" in matches[0]


@pytest.mark.asyncio
async def test_zero_trust_cert_and_differential_privacy():
    # X.509 cert validation
    cert = zero_trust_security.verify_device_certificate("AG-001")
    assert cert["x509_cert_valid"] is True
    assert "ATECC608A" in cert["hardware_root_of_trust"]

    # Differential privacy Laplace perturbation
    raw_cohort = [
        {"user_id": "patient_123", "pm2_5": 25.4, "aqi": 75},
        {"user_id": "patient_456", "pm2_5": 38.2, "aqi": 105}
    ]
    res = zero_trust_security.anonymize_with_differential_privacy(
        dataset_id="RESEARCH-COHORT-01",
        records=raw_cohort,
        epsilon=0.5
    )
    assert res["differential_privacy_guaranteed"] is True
    assert res["record_count"] == 2
    assert not res["anonymized_records"][0]["user_id"].startswith("patient_")
