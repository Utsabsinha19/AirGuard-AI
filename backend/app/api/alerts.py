"""
AirGuard AI - Multi-Channel Smart Alerting & Notification Center API (FR-5)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update

from backend.app.database import get_db, Alert
from backend.app.schemas import AlertResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    device_id: Optional[str] = None,
    unacknowledged_only: bool = False,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Lists alerts across all configured delivery channels."""
    stmt = select(Alert).order_by(Alert.acknowledged.asc(), desc(Alert.timestamp)).limit(limit)
    if device_id:
        stmt = stmt.where(Alert.device_id == device_id)
    if unacknowledged_only:
        stmt = stmt.where(Alert.acknowledged == False)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{alert_id}/ack", response_model=AlertResponse)
async def acknowledge_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Marks an alert as acknowledged by the user."""
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
    """Marks all alerts as acknowledged."""
    stmt = update(Alert).values(acknowledged=True)
    if device_id:
        stmt = stmt.where(Alert.device_id == device_id)
    await db.execute(stmt)
    await db.commit()
    return {"status": "success", "message": "All alerts acknowledged"}
