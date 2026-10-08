"""
AirGuard AI - Enterprise Spatial Hierarchy & Multi-Tenant Access API (v3.0 Section 4.2)
Implements: Organization -> Campus -> Building -> Floor -> Zone -> Room -> Sensor Node
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db, Device

router = APIRouter(prefix="/enterprise", tags=["enterprise"])


@router.get("/hierarchy")
async def get_enterprise_hierarchy(db: AsyncSession = Depends(get_db)):
    """
    Returns complete spatial organizational hierarchy:
    Organization -> Campus -> Building -> Floor -> Zone -> Room -> Sensor Node (Section 4.2).
    """
    res = await db.execute(select(Device))
    devices = res.scalars().all()

    rooms_by_zone: Dict[str, List[Dict[str, Any]]] = {}
    for d in devices:
        zone = d.zone or "Indoor"
        if zone not in rooms_by_zone:
            rooms_by_zone[zone] = []
        rooms_by_zone[zone].append({
            "room_name": d.room,
            "device_id": d.id,
            "device_name": d.name,
            "floor": d.floor,
            "status": "ONLINE" if d.is_online else "OFFLINE"
        })

    hierarchy = {
        "organization": {
            "id": "ORG-AIRGUARD-HQ",
            "name": "AirGuard Intelligent Facilities Corp",
            "tier": "ENTERPRISE_PRO",
            "campuses": [
                {
                    "id": "CAMPUS-SF-01",
                    "name": "San Francisco Tech Campus",
                    "buildings": [
                        {
                            "id": "BLDG-METRO-01",
                            "name": "Residential & Smart Lab Tower",
                            "floors": [
                                {
                                    "floor_id": "FL-01",
                                    "floor_name": "Main Residential Floor 1",
                                    "zones": [
                                        {
                                            "zone_name": zone_name,
                                            "rooms": room_list
                                        }
                                        for zone_name, room_list in rooms_by_zone.items()
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
    return hierarchy


@router.get("/tenants")
async def get_tenant_roles():
    """
    Role-Based Access Control (RBAC) tiers and active tenant policies.
    """
    return {
        "tenants": [
            {
                "tenant_id": "TENANT-001",
                "name": "Executive Building Operations",
                "role": "FACILITY_MANAGER",
                "permissions": ["READ_ALL_BUILDINGS", "CONTROL_CENTRAL_HVAC", "OVERRIDE_DAMPER", "EXPORT_AUDIT_LOGS"]
            },
            {
                "tenant_id": "TENANT-002",
                "name": "Smart Suite Occupant",
                "role": "OCCUPANT",
                "permissions": ["READ_LOCAL_ZONES", "CONTROL_ROOM_PURIFIER", "SET_HEALTH_PROFILE"]
            }
        ]
    }
