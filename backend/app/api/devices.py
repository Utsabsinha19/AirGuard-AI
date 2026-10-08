"""
AirGuard AI - Device Management & Multi-Room Allocation API (FR-6.2)
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db, Device, Telemetry
from backend.app.schemas import DeviceCreate, DeviceResponse, TelemetryResponse

router = APIRouter(prefix="/devices", tags=["devices"])


DEFAULT_DEVICES = [
    {
        "id": "AG-001",
        "name": "Master Bedroom Node",
        "room": "Master Bedroom",
        "floor": "2nd Floor",
        "ip_address": "192.168.1.101",
        "mac_address": "24:6F:28:AB:CD:01"
    },
    {
        "id": "AG-002",
        "name": "Living Room Monitor",
        "room": "Living Room",
        "floor": "1st Floor",
        "ip_address": "192.168.1.102",
        "mac_address": "24:6F:28:AB:CD:02"
    },
    {
        "id": "AG-003",
        "name": "Kitchen Air Sensor",
        "room": "Kitchen",
        "floor": "1st Floor",
        "ip_address": "192.168.1.103",
        "mac_address": "24:6F:28:AB:CD:03"
    },
    {
        "id": "AG-004",
        "name": "Home Office Station",
        "room": "Home Office",
        "floor": "2nd Floor",
        "ip_address": "192.168.1.104",
        "mac_address": "24:6F:28:AB:CD:04"
    }
]


async def ensure_default_devices_exist(db: AsyncSession):
    """Seed initial smart home multi-room devices if empty."""
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
                mac_address=dev_data["mac_address"]
            )
            db.add(device)
        await db.commit()


@router.get("", response_model=List[DeviceResponse])
async def list_devices(db: AsyncSession = Depends(get_db)):
    """Lists all registered IoT hardware nodes with their room assignment and latest telemetry."""
    await ensure_default_devices_exist(db)

    result = await db.execute(select(Device))
    devices = result.scalars().all()

    device_responses = []
    for d in devices:
        # Fetch latest telemetry for each device
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
            latest_telemetry=TelemetryResponse.from_orm(latest_tel) if latest_tel else None
        )
        device_responses.append(resp)

    return device_responses


@router.post("", response_model=DeviceResponse)
async def create_device(payload: DeviceCreate, db: AsyncSession = Depends(get_db)):
    """Registers a new edge node."""
    existing = await db.execute(select(Device).where(Device.id == payload.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Device with this ID already registered")

    new_device = Device(
        id=payload.id,
        name=payload.name,
        room=payload.room,
        floor=payload.floor or "Floor 1",
        firmware_version=payload.firmware_version or "v1.2.0",
        ip_address=payload.ip_address or "192.168.1.100",
        mac_address=payload.mac_address or "00:00:00:00:00:00",
        is_online=True,
        last_seen=datetime.utcnow()
    )
    db.add(new_device)
    await db.commit()
    await db.refresh(new_device)

    return DeviceResponse(
        id=new_device.id,
        name=new_device.name,
        room=new_device.room,
        floor=new_device.floor,
        is_online=new_device.is_online,
        last_seen=new_device.last_seen,
        firmware_version=new_device.firmware_version,
        ip_address=new_device.ip_address,
        mac_address=new_device.mac_address,
        latest_telemetry=None
    )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves a specific IoT device."""
    res = await db.execute(select(Device).where(Device.id == device_id))
    device = res.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    tel_res = await db.execute(
        select(Telemetry)
        .where(Telemetry.device_id == device.id)
        .order_by(desc(Telemetry.timestamp))
        .limit(1)
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
        latest_telemetry=TelemetryResponse.from_orm(latest_tel) if latest_tel else None
    )
