"""
AirGuard AI - Anomaly Detection & Root-Cause Diagnosis API (FR-4.3)
Answers core target questions:
1. "Why is it getting worse?"
2. "Is this unusual?"
3. "What should I do?"
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db, Anomaly, Telemetry
from backend.app.schemas import AnomalyResponse
from backend.app.ml.anomaly_engine import anomaly_engine

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("/diagnose/{device_id}")
async def get_live_diagnosis(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    Computes instantaneous root-cause diagnosis on the latest sensor telemetry.
    Cross-correlates multi-sensor metrics against rolling baseline to answer:
    - "Why is it getting worse?"
    - "Is this unusual?"
    - "What should I do?"
    """
    # Fetch recent readings for baseline comparison
    query = await db.execute(
        select(Telemetry)
        .where(Telemetry.device_id == device_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(30)
    )
    records = query.scalars().all()

    if not records:
        current_metrics = {
            "pm2_5": 8.0, "co2": 500.0, "voc": 80.0,
            "temperature": 22.0, "humidity": 45.0
        }
        hist_metrics = []
    else:
        latest = records[0]
        current_metrics = {
            "pm2_5": latest.calibrated_pm2_5,
            "co2": latest.co2,
            "voc": latest.calibrated_voc,
            "temperature": latest.temperature,
            "humidity": latest.humidity
        }
        hist_metrics = [
            {
                "pm2_5": r.calibrated_pm2_5,
                "co2": r.co2,
                "voc": r.calibrated_voc,
                "temperature": r.temperature,
                "humidity": r.humidity
            }
            for r in records[1:]
        ]

    diagnosis = anomaly_engine.detect_anomalies_and_diagnose(current_metrics, hist_metrics)
    return {
        "device_id": device_id,
        "timestamp": datetime.utcnow().isoformat(),
        **diagnosis
    }


@router.get("/history/{device_id}", response_model=List[AnomalyResponse])
async def get_anomaly_history(
    device_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves chronological log of logged anomalies and root-cause diagnoses."""
    query = await db.execute(
        select(Anomaly)
        .where(Anomaly.device_id == device_id)
        .order_by(desc(Anomaly.timestamp))
        .limit(limit)
    )
    records = query.scalars().all()
    return records
