"""
AirGuard AI - Interactive Virtual IoT Edge Node Simulator API
Enables live demonstration and validation of anomaly triggers,
offline flash buffer auto-flush, and multi-room pollution scenarios.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.schemas import TelemetryPayload
from backend.app.api.telemetry import ingest_telemetry

router = APIRouter(prefix="/simulator", tags=["simulator"])


class ScenarioTriggerRequest(BaseModel):
    scenario: str  # "COOKING_SMOKE", "POOR_VENTILATION", "CHEMICAL_CLEANER", "OPEN_WINDOW", "OFFLINE_BUFFER_BURST", "RESET_NOMINAL"
    device_id: str = "AG-001"


@router.post("/trigger")
async def trigger_scenario(req: ScenarioTriggerRequest, db: AsyncSession = Depends(get_db)):
    """
    Injects realistic environmental anomalies or simulates offline buffer flush.
    """
    scenario = req.scenario.upper()
    dev_id = req.device_id
    now = datetime.utcnow()

    if scenario == "COOKING_SMOKE":
        # Simultaneous PM2.5 + VOC spike
        payload = TelemetryPayload(
            device_id=dev_id,
            timestamp=now,
            pm2_5=68.5,
            pm10=95.0,
            co2=720.0,
            voc=485.0,
            temperature=24.5,
            humidity=62.0,
            pressure=1012.5
        )
        await ingest_telemetry(payload, db)
        return {
            "status": "success",
            "scenario": scenario,
            "device_id": dev_id,
            "message": "Injected Cooking Smoke event (High PM2.5: 68.5 µg/m³, High VOC: 485 ppb)."
        }

    elif scenario == "POOR_VENTILATION":
        # Elevated CO2 + VOC, baseline PM
        payload = TelemetryPayload(
            device_id=dev_id,
            timestamp=now,
            pm2_5=8.2,
            pm10=12.0,
            co2=1580.0,
            voc=390.0,
            temperature=23.8,
            humidity=55.0,
            pressure=1013.0
        )
        await ingest_telemetry(payload, db)
        return {
            "status": "success",
            "scenario": scenario,
            "device_id": dev_id,
            "message": "Injected Poor Ventilation event (High CO2: 1580 ppm, High VOC: 390 ppb)."
        }

    elif scenario == "CHEMICAL_CLEANER":
        # Isolated VOC spike
        payload = TelemetryPayload(
            device_id=dev_id,
            timestamp=now,
            pm2_5=6.5,
            pm10=9.0,
            co2=510.0,
            voc=720.0,
            temperature=21.8,
            humidity=46.0,
            pressure=1013.2
        )
        await ingest_telemetry(payload, db)
        return {
            "status": "success",
            "scenario": scenario,
            "device_id": dev_id,
            "message": "Injected Chemical Cleaner/Solvent spike (Extreme VOC: 720 ppb, clean PM2.5)."
        }

    elif scenario == "OPEN_WINDOW":
        # Fresh air rapid dilution
        payload = TelemetryPayload(
            device_id=dev_id,
            timestamp=now,
            pm2_5=5.4,
            pm10=8.0,
            co2=430.0,
            voc=65.0,
            temperature=20.5,
            humidity=44.0,
            pressure=1014.0
        )
        await ingest_telemetry(payload, db)
        return {
            "status": "success",
            "scenario": scenario,
            "device_id": dev_id,
            "message": "Injected Fresh Air Window Opening (PM2.5: 5.4, CO2: 430 ppm, VOC: 65 ppb)."
        }

    elif scenario == "OFFLINE_BUFFER_BURST":
        # Simulates firmware reconnecting after Wi-Fi drop and draining 8 buffered records
        results = []
        for i in range(8, 0, -1):
            past_ts = now - timedelta(seconds=i * 5)
            buf_payload = TelemetryPayload(
                device_id=dev_id,
                timestamp=past_ts,
                pm2_5=14.0 + (8 - i) * 1.5,
                pm10=20.0 + (8 - i) * 2.0,
                co2=680.0 + (8 - i) * 30.0,
                voc=130.0 + (8 - i) * 15.0,
                temperature=22.0,
                humidity=48.0,
                pressure=1013.0
            )
            res = await ingest_telemetry(buf_payload, db)
            results.append(res.id)
        return {
            "status": "success",
            "scenario": scenario,
            "device_id": dev_id,
            "flushed_records_count": len(results),
            "message": f"Successfully flushed {len(results)} buffered readings accumulated during simulated Wi-Fi outage (FR-2.3)."
        }

    elif scenario == "RESET_NOMINAL":
        # Restores standard nominal state
        payload = TelemetryPayload(
            device_id=dev_id,
            timestamp=now,
            pm2_5=9.0,
            pm10=14.0,
            co2=580.0,
            voc=95.0,
            temperature=22.2,
            humidity=46.0,
            pressure=1013.25
        )
        await ingest_telemetry(payload, db)
        return {
            "status": "success",
            "scenario": scenario,
            "device_id": dev_id,
            "message": "Reset device to nominal clean indoor baseline."
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown scenario '{scenario}'")
