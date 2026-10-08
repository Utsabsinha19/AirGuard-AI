"""
AirGuard AI - Telemetry Ingestion & Query API (FR-3.3, FR-3.4, NFR-1)
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db, Telemetry, Device, Anomaly, Alert, RemediationAction
from backend.app.schemas import TelemetryPayload, TelemetryResponse
from backend.app.ml.calibration import calibrate_pm25, calibrate_voc, compute_comprehensive_aqi
from backend.app.ml.anomaly_engine import anomaly_engine
from backend.app.websocket_manager import ws_manager
from backend.app.config import settings

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("/ingest", response_model=TelemetryResponse)
async def ingest_telemetry(payload: TelemetryPayload, db: AsyncSession = Depends(get_db)):
    """
    Ingests raw sensor stream from ESP32 edge node or virtual simulator.
    Performs non-linear cross-calibration, computes EPA AQI, detects anomalies,
    updates devices, and broadcasts via WebSockets (<1s latency).
    """
    ts = payload.timestamp or datetime.utcnow()

    # 1. Non-linear calibration
    cal_pm25 = calibrate_pm25(payload.pm2_5, payload.humidity, payload.temperature)
    cal_voc = calibrate_voc(payload.voc, payload.temperature, payload.humidity)

    # 2. Comprehensive EPA AQI computation
    aqi_result = compute_comprehensive_aqi(
        pm25=cal_pm25,
        pm10=payload.pm10,
        co2=payload.co2,
        voc=cal_voc
    )

    # 3. Ensure device exists in database
    dev_query = await db.execute(select(Device).where(Device.id == payload.device_id))
    device = dev_query.scalar_one_or_none()
    if not device:
        # Auto-register new node
        device = Device(
            id=payload.device_id,
            name=f"AirGuard Node ({payload.device_id})",
            room="General Living Area",
            is_online=True,
            last_seen=ts
        )
        db.add(device)
    else:
        device.is_online = True
        device.last_seen = ts

    # 4. Save Telemetry record
    telemetry_record = Telemetry(
        device_id=payload.device_id,
        timestamp=ts,
        pm2_5=payload.pm2_5,
        pm10=payload.pm10 or (payload.pm2_5 * 1.4),
        co2=payload.co2,
        voc=payload.voc,
        temperature=payload.temperature,
        humidity=payload.humidity,
        pressure=payload.pressure or 1013.25,
        calibrated_pm2_5=cal_pm25,
        calibrated_voc=cal_voc,
        aqi=aqi_result["aqi"],
        aqi_category=aqi_result["category"],
        dominant_pollutant=aqi_result["dominant_pollutant"]
    )
    db.add(telemetry_record)

    # 5. Anomaly Detection & Root-Cause Diagnosis
    current_metrics = {
        "pm2_5": cal_pm25,
        "pm10": payload.pm10,
        "co2": payload.co2,
        "voc": cal_voc,
        "temperature": payload.temperature,
        "humidity": payload.humidity
    }
    diag = anomaly_engine.detect_anomalies_and_diagnose(current_metrics)

    if diag["is_anomaly"] and diag["severity"] in ["MEDIUM", "HIGH", "CRITICAL"]:
        anomaly_record = Anomaly(
            device_id=payload.device_id,
            timestamp=ts,
            anomaly_score=diag["anomaly_score"],
            severity=diag["severity"],
            root_cause_code=diag["root_cause_code"],
            root_cause_title=diag["root_cause_title"],
            description=diag["description"],
            recommendation=diag["recommendation"],
            sensor_contributions=diag["sensor_contributions"]
        )
        db.add(anomaly_record)

        # Trigger Smart Alert (FR-5)
        alert_level = "CRITICAL" if diag["severity"] == "CRITICAL" else "WARNING"
        alert_record = Alert(
            device_id=payload.device_id,
            timestamp=ts,
            level=alert_level,
            channel="DASHBOARD",
            title=f"{diag['root_cause_title']} Detected ({payload.device_id})",
            message=diag["description"],
            recommendation=diag["recommendation"]
        )
        db.add(alert_record)

        # Push immediate WebSocket alert
        await ws_manager.broadcast_alert({
            "device_id": payload.device_id,
            "title": alert_record.title,
            "level": alert_level,
            "message": alert_record.message,
            "recommendation": alert_record.recommendation,
            "timestamp": ts.isoformat()
        })

    # 6. Update Active Remediation Actions (Closed-Loop Tracker FR-6.2)
    act_query = await db.execute(
        select(RemediationAction).where(
            RemediationAction.device_id == payload.device_id,
            RemediationAction.is_active == True
        )
    )
    active_action = act_query.scalar_one_or_none()
    if active_action:
        active_action.current_aqi = aqi_result["aqi"]
        if aqi_result["aqi"] <= active_action.target_aqi + 5:
            # Resolved!
            active_action.is_active = False
            active_action.resolved_at = ts
            duration = (ts - active_action.timestamp).total_seconds() / 60.0
            active_action.recovery_duration_mins = round(duration, 1)
            # Efficacy score: reduction relative to initial delta
            reduction = active_action.initial_aqi - aqi_result["aqi"]
            initial_delta = max(1, active_action.initial_aqi - active_action.target_aqi)
            active_action.efficacy_score = round(min(100.0, max(0.0, (reduction / initial_delta) * 100.0)), 1)

    await db.commit()
    await db.refresh(telemetry_record)

    # 7. Sub-second WebSocket Broadcast (NFR-1)
    broadcast_data = {
        "type": "TELEMETRY_UPDATE",
        "device_id": payload.device_id,
        "timestamp": ts.isoformat(),
        "pm2_5": payload.pm2_5,
        "pm10": telemetry_record.pm10,
        "co2": payload.co2,
        "voc": payload.voc,
        "temperature": payload.temperature,
        "humidity": payload.humidity,
        "pressure": payload.pressure,
        "calibrated_pm2_5": cal_pm25,
        "calibrated_voc": cal_voc,
        "aqi": aqi_result["aqi"],
        "aqi_category": aqi_result["category"],
        "aqi_color": aqi_result["color"],
        "dominant_pollutant": aqi_result["dominant_pollutant"],
        "diagnosis": diag
    }
    await ws_manager.broadcast_telemetry(broadcast_data)

    return telemetry_record


@router.get("/latest/{device_id}", response_model=TelemetryResponse)
async def get_latest_telemetry(device_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves the most recent telemetry measurement for a specific device."""
    query = await db.execute(
        select(Telemetry)
        .where(Telemetry.device_id == device_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(1)
    )
    latest = query.scalar_one_or_none()
    if not latest:
        raise HTTPException(status_code=404, detail="No telemetry found for device")
    return latest


@router.get("/history/{device_id}", response_model=List[TelemetryResponse])
async def get_telemetry_history(
    device_id: str,
    limit: int = Query(60, ge=5, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves historical chronological telemetry for trend charts."""
    query = await db.execute(
        select(Telemetry)
        .where(Telemetry.device_id == device_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(limit)
    )
    records = query.scalars().all()
    # Return chronologically ascending for charts
    return list(reversed(records))
