"""
AirGuard AI - Smart Home Actuation & Automation API (Matter & Home Assistant, v3.0 Section 3.1)
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db, ActuatorDevice, ActuationLog
from backend.app.schemas import ActuatorResponse, ActuationLogResponse, ActuatorControlRequest
from backend.app.actuation.engine import actuation_engine

router = APIRouter(prefix="/actuation", tags=["actuation"])


@router.get("/devices", response_model=List[ActuatorResponse])
async def get_actuator_devices(db: AsyncSession = Depends(get_db)):
    """
    Returns list of all registered Matter and Home Assistant actuators.
    """
    await actuation_engine.init_default_actuators(db)
    query = await db.execute(select(ActuatorDevice))
    return query.scalars().all()


@router.post("/control", response_model=ActuatorResponse)
async def control_actuator(req: ActuatorControlRequest, db: AsyncSession = Depends(get_db)):
    """
    Manually controls a Matter or Home Assistant smart home actuator.
    """
    query = await db.execute(select(ActuatorDevice).where(ActuatorDevice.id == req.actuator_id))
    actuator = query.scalar_one_or_none()
    if not actuator:
        raise HTTPException(status_code=404, detail=f"Actuator {req.actuator_id} not found")

    now = datetime.utcnow()
    action_desc = []

    if req.state is not None:
        actuator.state = req.state
        action_desc.append(f"State -> {req.state}")
    if req.fan_speed is not None:
        actuator.fan_speed = req.fan_speed
        action_desc.append(f"Fan -> {req.fan_speed}")
    if req.damper_position is not None:
        actuator.damper_position = max(0, min(100, req.damper_position))
        action_desc.append(f"Damper -> {actuator.damper_position}%")
    if req.window_open_pct is not None:
        actuator.window_open_pct = max(0, min(100, req.window_open_pct))
        actuator.state = "OPEN" if actuator.window_open_pct > 0 else "CLOSED"
        action_desc.append(f"Window -> {actuator.window_open_pct}%")
    if req.auto_mode is not None:
        actuator.auto_mode = req.auto_mode
        action_desc.append(f"AutoMode -> {req.auto_mode}")

    actuator.last_actuated_at = now

    log = ActuationLog(
        actuator_id=actuator.id,
        timestamp=now,
        trigger_type="MANUAL_OVERRIDE",
        action_taken=", ".join(action_desc) if action_desc else "Parameter Update",
        reason="User requested manual actuation via dashboard control panel",
        status="SUCCESS"
    )
    db.add(log)
    await db.commit()
    await db.refresh(actuator)

    return actuator


@router.get("/logs", response_model=List[ActuationLogResponse])
async def get_actuation_logs(limit: int = 25, db: AsyncSession = Depends(get_db)):
    """
    Returns chronological audit log of closed-loop smart home actuation events.
    """
    query = await db.execute(
        select(ActuationLog)
        .order_by(desc(ActuationLog.timestamp))
        .limit(limit)
    )
    return query.scalars().all()


@router.post("/evaluate")
async def trigger_actuation_evaluation(room: str = "Living Room", db: AsyncSession = Depends(get_db)):
    """
    Manually triggers smart home rule evaluation across room actuators.
    """
    actions = await actuation_engine.evaluate_and_actuate(
        room=room,
        current_pm25=42.0,
        current_co2=1350.0,
        predicted_pm25_15m=52.0,
        outdoor_aqi=40,
        session=db
    )
    return {"status": "success", "evaluated_room": room, "actions_taken": actions}
