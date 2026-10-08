"""
AirGuard AI - Multi-Channel Smart Alerting & Notification Center API (FR-5, Section 2.3)
Enhanced with Interactive Recommendation Workflows:
Allows converting smart alerts directly into active remediation tracking sessions.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update

from backend.app.database import get_db, Alert, RemediationAction, Telemetry
from backend.app.schemas import AlertResponse, ActionResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    device_id: Optional[str] = None,
    unacknowledged_only: bool = False,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Alert).order_by(Alert.acknowledged.asc(), desc(Alert.timestamp)).limit(limit)
    if device_id:
        stmt = stmt.where(Alert.device_id == device_id)
    if unacknowledged_only:
        stmt = stmt.where(Alert.acknowledged == False)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{alert_id}/ack", response_model=AlertResponse)
async def acknowledge_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True
    await db.commit()
    await db.refresh(alert)
    return alert


@router.post("/ack-all")
async def acknowledge_all_alerts(device_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    stmt = update(Alert).values(acknowledged=True)
    if device_id:
        stmt = stmt.where(Alert.device_id == device_id)
    await db.execute(stmt)
    await db.commit()
    return {"status": "success", "message": "All alerts acknowledged"}


@router.post("/{alert_id}/convert-to-action", response_model=ActionResponse)
async def convert_alert_to_action(alert_id: int, db: AsyncSession = Depends(get_db)):
    """
    Transforms a smart alert into an interactive remediation tracking workflow (Section 2.3).
    Marks alert as acknowledged and initializes recovery curve tracking.
    """
    res = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True

    # Fetch current telemetry
    tel_res = await db.execute(
        select(Telemetry).where(Telemetry.device_id == alert.device_id).order_by(desc(Telemetry.timestamp)).limit(1)
    )
    latest_tel = tel_res.scalar_one_or_none()
    cur_aqi = latest_tel.aqi if latest_tel else 115
    cur_pm = latest_tel.calibrated_pm2_5 if latest_tel else 42.0
    cur_co2 = latest_tel.co2 if latest_tel else 1250.0

    # Deactivate any previous ongoing actions for this device
    prev_query = await db.execute(
        select(RemediationAction).where(
            RemediationAction.device_id == alert.device_id,
            RemediationAction.is_active == True
        )
    )
    for prev in prev_query.scalars().all():
        prev.is_active = False

    action = RemediationAction(
        device_id=alert.device_id,
        timestamp=datetime.utcnow(),
        action_type="ALERT_INTERVENTION",
        description=f"Action taken for: {alert.title}",
        initial_aqi=cur_aqi,
        initial_pm2_5=cur_pm,
        initial_co2=cur_co2,
        current_aqi=cur_aqi,
        target_aqi=50,
        is_active=True
    )
    db.add(action)
    await db.commit()
    await db.refresh(action)
    return action
