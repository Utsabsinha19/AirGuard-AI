"""
AirGuard AI - Device Management & Multi-Room Allocation API (FR-6.2, Section 2.2, 2.3)
Enhanced with:
- Floorplan spatial coordinates (x_coord, y_coord, latitude, longitude)
- Device-level auto-calibration adjustments (zero-point offset and gain factor)
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db, Device, Telemetry
from backend.app.schemas import DeviceCreate, DeviceResponse, DeviceCalibrationRequest, TelemetryResponse

router = APIRouter(prefix="/devices", tags=["devices"])


DEFAULT_DEVICES = [
    {
        "id": "AG-001",
        "name": "Master Bedroom Node",
        "room": "Master Bedroom",
        "floor": "2nd Floor",
        "ip_address": "192.168.1.101",
        "mac_address": "24:6F:28:AB:CD:01",
        "x_coord": 25.0,
        "y_coord": 30.0,
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    {
        "id": "AG-002",
        "name": "Living Room Monitor",
        "room": "Living Room",
        "floor": "1st Floor",
        "ip_address": "192.168.1.102",
        "mac_address": "24:6F:28:AB:CD:02",
        "x_coord": 75.0,
        "y_coord": 35.0,
        "latitude": 37.7749,
        "longitude": -122.4192
    },
    {
        "id": "AG-003",
        "name": "Kitchen Air Sensor",
        "room": "Kitchen",
        "floor": "1st Floor",
        "ip_address": "192.168.1.103",
        "mac_address": "24:6F:28:AB:CD:03",
        "x_coord": 70.0,
        "y_coord": 75.0,
        "latitude": 37.7748,
        "longitude": -122.4193
    },
    {
        "id": "AG-004",
        "name": "Home Office Station",
        "room": "Home Office",
        "floor": "2nd Floor",
        "ip_address": "192.168.1.104",
        "mac_address": "24:6F:28:AB:CD:04",
        "x_coord": 30.0,
        "y_coord": 70.0,
        "latitude": 37.7750,
        "longitude": -122.4195
    }
]


async def ensure_default_devices_exist(db: AsyncSession):
    res = await db.execute(select(Device).limit(1))
    if res.scalar_one_or_none() is None:
        for dev_data in DEFAULT_DEVICES:
            device = Device(
                id=dev_data["id"],
                name=dev_data["name"],
                room=dev_data["room"],
                floor=dev_data["floor"],
                is_online=True,
                last_seen=datetime.utcnow(),
                ip_address=dev_data["ip_address"],
                mac_address=dev_data["mac_address"],
                x_coord=dev_data["x_coord"],
                y_coord=dev_data["y_coord"],
                latitude=dev_data["latitude"],
                longitude=dev_data["longitude"]
            )
            db.add(device)
        await db.commit()


@router.get("", response_model=List[DeviceResponse])
async def list_devices(db: AsyncSession = Depends(get_db)):
    await ensure_default_devices_exist(db)

    result = await db.execute(select(Device))
    devices = result.scalars().all()

    device_responses = []
    for d in devices:
        tel_res = await db.execute(
            select(Telemetry)
            .where(Telemetry.device_id == d.id)
            .order_by(desc(Telemetry.timestamp))
            .limit(1)
        )
        latest_tel = tel_res.scalar_one_or_none()

        resp = DeviceResponse(
            id=d.id,
            name=d.name,
            room=d.room,
            floor=d.floor or "Floor 1",
            is_online=d.is_online,
            last_seen=d.last_seen,
            firmware_version=d.firmware_version,
            ip_address=d.ip_address,
            mac_address=d.mac_address,
            x_coord=d.x_coord or 25.0,
            y_coord=d.y_coord or 30.0,
            latitude=d.latitude or 37.7749,
            longitude=d.longitude or -122.4194,
            pm_zero_offset=d.pm_zero_offset or 0.0,
            pm_gain=d.pm_gain or 1.0,
            voc_zero_offset=d.voc_zero_offset or 0.0,
            voc_gain=d.voc_gain or 1.0,
            latest_telemetry=TelemetryResponse.from_orm(latest_tel) if latest_tel else None
        )
        device_responses.append(resp)

    return device_responses


@router.post("/{device_id}/calibrate", response_model=DeviceResponse)
async def calibrate_device(
    device_id: str,
    req: DeviceCalibrationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Sets device-level zero-point calibration offset and gain scaling factors (Section 2.2).
    """
    res = await db.execute(select(Device).where(Device.id == device_id))
    device = res.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if req.pm_zero_offset is not None:
        device.pm_zero_offset = req.pm_zero_offset
    if req.pm_gain is not None:
        device.pm_gain = req.pm_gain
    if req.voc_zero_offset is not None:
        device.voc_zero_offset = req.voc_zero_offset
    if req.voc_gain is not None:
        device.voc_gain = req.voc_gain

    await db.commit()
    await db.refresh(device)

    tel_res = await db.execute(
        select(Telemetry).where(Telemetry.device_id == device.id).order_by(desc(Telemetry.timestamp)).limit(1)
    )
    latest_tel = tel_res.scalar_one_or_none()

    return DeviceResponse(
        id=device.id,
        name=device.name,
        room=device.room,
        floor=device.floor,
        is_online=device.is_online,
        last_seen=device.last_seen,
        firmware_version=device.firmware_version,
        ip_address=device.ip_address,
        mac_address=device.mac_address,
        x_coord=device.x_coord,
        y_coord=device.y_coord,
        latitude=device.latitude,
        longitude=device.longitude,
        pm_zero_offset=device.pm_zero_offset,
        pm_gain=device.pm_gain,
        voc_zero_offset=device.voc_zero_offset,
        voc_gain=device.voc_gain,
        latest_telemetry=TelemetryResponse.from_orm(latest_tel) if latest_tel else None
    )
