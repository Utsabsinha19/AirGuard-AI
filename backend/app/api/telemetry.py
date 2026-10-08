"""
AirGuard AI - Telemetry Ingestion & Query API (FR-3.3, FR-3.4, NFR-1, Section 2.1, 2.3)
Enhanced with:
- Expanded sensor parameters: Barometric Pressure, Ambient Light, Noise Level, Battery %
- Device-specific zero offset & gain calibration
- CSV telemetry export for environmental compliance & reporting
"""

from datetime import datetime
import io
import csv
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db, Telemetry, Device, Anomaly, Alert, RemediationAction
from backend.app.schemas import TelemetryPayload, TelemetryResponse
from backend.app.ml.calibration import calibrate_pm25, calibrate_voc, compute_comprehensive_aqi
from backend.app.ml.anomaly_engine import anomaly_engine
from backend.app.websocket_manager import ws_manager

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("/ingest", response_model=TelemetryResponse)
async def ingest_telemetry(payload: TelemetryPayload, db: AsyncSession = Depends(get_db)):
    ts = payload.timestamp or datetime.utcnow()

    # 1. Fetch device calibration factors if device exists
    dev_query = await db.execute(select(Device).where(Device.id == payload.device_id))
    device = dev_query.scalar_one_or_none()
    
    pm_offset, pm_gain = 0.0, 1.0
    voc_offset, voc_gain = 0.0, 1.0

    if not device:
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
        pm_offset = device.pm_zero_offset or 0.0
        pm_gain = device.pm_gain or 1.0
        voc_offset = device.voc_zero_offset or 0.0
        voc_gain = device.voc_gain or 1.0

    # 2. Non-linear calibration with device gain/offset
    cal_pm25 = calibrate_pm25(
        raw_pm25=payload.pm2_5,
        humidity_rh=payload.humidity,
        temp_c=payload.temperature,
        zero_offset=pm_offset,
        gain_scale=pm_gain
    )
    cal_voc = calibrate_voc(
        raw_voc_ppb=payload.voc,
        temp_c=payload.temperature,
        humidity_rh=payload.humidity,
        zero_offset=voc_offset,
        gain_scale=voc_gain
    )

    # 3. Comprehensive EPA AQI computation
    aqi_result = compute_comprehensive_aqi(
        pm25=cal_pm25,
        pm10=payload.pm10,
        co2=payload.co2,
        voc=cal_voc
    )

    # 4. Save Telemetry record with expanded metrics
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
        ambient_light=payload.ambient_light or 150.0,
        noise_level=payload.noise_level or 42.0,
        battery_pct=payload.battery_pct or 95,
        calibrated_pm2_5=cal_pm25,
        calibrated_voc=cal_voc,
        aqi=aqi_result["aqi"],
        aqi_category=aqi_result["category"],
        dominant_pollutant=aqi_result["dominant_pollutant"]
    )
    db.add(telemetry_record)

    # 5. Context-aware Anomaly Detection
    current_metrics = {
        "pm2_5": cal_pm25,
        "pm10": payload.pm10,
        "co2": payload.co2,
        "voc": cal_voc,
        "temperature": payload.temperature,
        "humidity": payload.humidity,
        "pressure": payload.pressure,
        "ambient_light": payload.ambient_light,
        "noise_level": payload.noise_level
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

        alert_level = "CRITICAL" if diag["severity"] == "CRITICAL" else "WARNING"
        alert_record = Alert(
            device_id=payload.device_id,
            timestamp=ts,
            level=alert_level,
            channel="DASHBOARD",
            title=f"{diag['root_cause_title']} ({payload.device_id})",
            message=diag["description"],
            recommendation=diag["recommendation"]
        )
        db.add(alert_record)

        await ws_manager.broadcast_alert({
            "id": 9999,
            "device_id": payload.device_id,
            "title": alert_record.title,
            "level": alert_level,
            "message": alert_record.message,
            "recommendation": alert_record.recommendation,
            "timestamp": ts.isoformat()
        })

    # 6. Update Active Remediation Actions
    act_query = await db.execute(
        select(RemediationAction).where(
            RemediationAction.device_id == payload.device_id,
            RemediationAction.is_active == True
        )
    )
    active_actions = act_query.scalars().all()
    for active_action in active_actions:
        active_action.current_aqi = aqi_result["aqi"]
        if aqi_result["aqi"] <= active_action.target_aqi + 5:
            active_action.is_active = False
            active_action.resolved_at = ts
            duration = (ts - active_action.timestamp).total_seconds() / 60.0
            active_action.recovery_duration_mins = round(duration, 1)
            reduction = active_action.initial_aqi - aqi_result["aqi"]
            initial_delta = max(1, active_action.initial_aqi - active_action.target_aqi)
            active_action.efficacy_score = round(min(100.0, max(0.0, (reduction / initial_delta) * 100.0)), 1)

    await db.commit()
    await db.refresh(telemetry_record)

    # 7. Sub-second WebSocket Broadcast
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
        "pressure": telemetry_record.pressure,
        "ambient_light": telemetry_record.ambient_light,
        "noise_level": telemetry_record.noise_level,
        "battery_pct": telemetry_record.battery_pct,
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
    query = await db.execute(
        select(Telemetry)
        .where(Telemetry.device_id == device_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(limit)
    )
    records = query.scalars().all()
    return list(reversed(records))


@router.get("/export/{device_id}")
async def export_telemetry_csv(device_id: str, db: AsyncSession = Depends(get_db)):
    """Exports historical telemetry as downloadable CSV (Section 2.1)."""
    query = await db.execute(
        select(Telemetry)
        .where(Telemetry.device_id == device_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(2000)
    )
    records = query.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "timestamp", "device_id", "pm2_5", "pm10", "co2", "voc",
        "temperature", "humidity", "pressure", "ambient_light", "noise_level",
        "calibrated_pm2_5", "calibrated_voc", "aqi", "aqi_category"
    ])

    for r in reversed(records):
        writer.writerow([
            r.timestamp.isoformat(), r.device_id, r.pm2_5, r.pm10, r.co2, r.voc,
            r.temperature, r.humidity, r.pressure, r.ambient_light, r.noise_level,
            r.calibrated_pm2_5, r.calibrated_voc, r.aqi, r.aqi_category
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=airguard_{device_id}_export.csv"}
    )
