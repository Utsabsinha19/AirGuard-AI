"""
AirGuard AI - Closed-Loop Remediation Action Tracker API (FR-6.2)
Tracks user interventions (e.g. "Opened window", "Turned on HEPA purifier")
and quantifies real-time atmospheric recovery curves and efficacy scores.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db, RemediationAction, Telemetry
from backend.app.schemas import ActionCreate, ActionResponse

router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("/log", response_model=ActionResponse)
async def log_remediation_action(payload: ActionCreate, db: AsyncSession = Depends(get_db)):
    """
    Logs an intervention by the user (e.g., 'Opened window', 'Activated HEPA filter')
    and initializes real-time tracking of atmospheric recovery.
    """
    # Fetch latest telemetry to establish initial pre-action baseline
    tel_res = await db.execute(
        select(Telemetry)
        .where(Telemetry.device_id == payload.device_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(1)
    )
    latest_tel = tel_res.scalar_one_or_none()

    cur_aqi = latest_tel.aqi if latest_tel else 110
    cur_pm = latest_tel.calibrated_pm2_5 if latest_tel else 38.0
    cur_co2 = latest_tel.co2 if latest_tel else 1250.0

    # Deactivate any previous ongoing actions for this device
    prev_query = await db.execute(
        select(RemediationAction).where(
            RemediationAction.device_id == payload.device_id,
            RemediationAction.is_active == True
        )
    )
    for prev in prev_query.scalars().all():
        prev.is_active = False

    action = RemediationAction(
        device_id=payload.device_id,
        timestamp=datetime.utcnow(),
        action_type=payload.action_type,
        description=payload.description,
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


@router.get("/active/{device_id}", response_model=Optional[ActionResponse])
async def get_active_action(device_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves ongoing remediation recovery action for device."""
    res = await db.execute(
        select(RemediationAction)
        .where(
            RemediationAction.device_id == device_id,
            RemediationAction.is_active == True
        )
        .order_by(desc(RemediationAction.timestamp))
        .limit(1)
    )
    return res.scalar_one_or_none()


@router.get("/history/{device_id}", response_model=List[ActionResponse])
async def get_action_history(device_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves log of completed remediation actions and their efficacy scores."""
    res = await db.execute(
        select(RemediationAction)
        .where(RemediationAction.device_id == device_id)
        .order_by(desc(RemediationAction.timestamp))
        .limit(20)
    )
    return res.scalars().all()


@router.post("/{action_id}/resolve", response_model=ActionResponse)
async def resolve_action(action_id: int, db: AsyncSession = Depends(get_db)):
    """Manually completes an active remediation action."""
    res = await db.execute(select(RemediationAction).where(RemediationAction.id == action_id))
    action = res.scalar_one_or_none()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    action.is_active = False
    action.resolved_at = datetime.utcnow()
    duration = (action.resolved_at - action.timestamp).total_seconds() / 60.0
    action.recovery_duration_mins = round(duration, 1)

    reduction = action.initial_aqi - action.current_aqi
    initial_delta = max(1, action.initial_aqi - action.target_aqi)
    action.efficacy_score = round(min(100.0, max(0.0, (reduction / initial_delta) * 100.0)), 1)

    duration_mins = max(0.1, duration)
    co2_delta = action.initial_co2 - (action.current_co2 or action.initial_co2)
    pm_delta = action.initial_pm2_5 - (action.current_pm2_5 or action.initial_pm2_5)
    action.co2_decay_rate = round(co2_delta / duration_mins, 2)
    action.pm25_decay_rate = round(pm_delta / duration_mins, 2)
    action.recovery_message = f"CO2 returned to {int(action.current_co2 or 700)} ppm in {action.recovery_duration_mins} minutes (Decay rate: {action.co2_decay_rate} ppm/min)"

    await db.commit()
    await db.refresh(action)
    return action
