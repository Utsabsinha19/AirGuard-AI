"""
AirGuard AI - Personal Inhalation Exposure & Health Risk Analytics API (v3.0 Section 5.1, 5.2)
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db, UserHealthProfile
from backend.app.schemas import (
    ExposureMetricsResponse,
    HealthProfileResponse,
    HealthProfileUpdateRequest
)
from backend.app.health.exposure_engine import exposure_engine, PROFILE_DEFAULTS

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/exposure", response_model=ExposureMetricsResponse)
async def get_cumulative_exposure(
    user_id: str = "default_user",
    window_hours: float = Query(24.0, ge=1.0, le=168.0),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculates cumulative inhalation dosage (I_pollutant = sum(C_i * V_E * Delta_t_i))
    and personal health risk score according to clinical profile limits.
    """
    res = await exposure_engine.calculate_exposure(user_id, window_hours, db)
    return ExposureMetricsResponse(**res)


@router.post("/profile", response_model=HealthProfileResponse)
async def update_health_profile(
    req: HealthProfileUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates user health profile type (STANDARD, ASTHMATIC, CARDIOVASCULAR, PEDIATRIC, ELDERLY)
    and customizes respiratory sensitivity limits.
    """
    p_type = req.profile_type.upper()
    if p_type not in PROFILE_DEFAULTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid profile '{p_type}'. Must be one of: {list(PROFILE_DEFAULTS.keys())}"
        )

    profile = await exposure_engine.get_or_create_profile(req.user_id or "default_user", db)
    defs = PROFILE_DEFAULTS[p_type]

    profile.profile_type = p_type
    profile.minute_ventilation_rate = req.minute_ventilation_rate or defs["minute_ventilation_rate"]
    profile.target_pm25_limit = req.target_pm25_limit or defs["target_pm25_limit"]
    profile.target_co2_limit = req.target_co2_limit or defs["target_co2_limit"]
    profile.target_hcho_limit = req.target_hcho_limit or defs["target_hcho_limit"]

    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/profiles")
async def list_health_profiles():
    """
    Returns available clinical profile archetypes and descriptions.
    """
    return PROFILE_DEFAULTS
