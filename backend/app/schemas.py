"""
AirGuard AI - Pydantic Request & Response Data Schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Telemetry Schemas
# ---------------------------------------------------------------------------

class TelemetryPayload(BaseModel):
    """Payload received from IoT Edge Node (FR-3.3)"""
    device_id: str = Field(..., example="AG-001")
    timestamp: Optional[datetime] = None
    pm2_5: float = Field(..., ge=0, example=12.5)
    pm10: Optional[float] = Field(None, ge=0, example=18.2)
    co2: float = Field(..., ge=300, le=10000, example=720.0)
    voc: float = Field(..., ge=0, example=145.0)
    temperature: float = Field(..., example=22.4)
    humidity: float = Field(..., ge=0, le=100, example=48.2)
    pressure: Optional[float] = Field(1013.25, example=1012.8)


class TelemetryResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    pm2_5: float
    pm10: Optional[float]
    co2: float
    voc: float
    temperature: float
    humidity: float
    pressure: Optional[float]
    calibrated_pm2_5: float
    calibrated_voc: float
    aqi: int
    aqi_category: str
    dominant_pollutant: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Device Schemas
# ---------------------------------------------------------------------------

class DeviceCreate(BaseModel):
    id: str = Field(..., example="AG-001")
    name: str = Field(..., example="Master Bedroom Sensor")
    room: str = Field(..., example="Bedroom")
    floor: Optional[str] = "Floor 1"
    firmware_version: Optional[str] = "v1.2.0"
    ip_address: Optional[str] = "192.168.1.101"
    mac_address: Optional[str] = "24:6F:28:AB:CD:01"


class DeviceResponse(BaseModel):
    id: str
    name: str
    room: str
    floor: str
    is_online: bool
    last_seen: datetime
    firmware_version: str
    ip_address: str
    mac_address: str
    latest_telemetry: Optional[TelemetryResponse] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Prediction Schemas
# ---------------------------------------------------------------------------

class HorizonPrediction(BaseModel):
    model_config = {"protected_namespaces": ()}
    horizon_mins: int
    horizon_label: str
    predicted_pm2_5: float
    predicted_co2: int
    predicted_voc: int
    predicted_aqi: int
    aqi_category: str
    aqi_color: str
    dominant_pollutant: str
    confidence_lower: float
    confidence_upper: float
    model_type: str


class PredictionResponse(BaseModel):
    device_id: str
    current_aqi: int
    current_category: str
    generated_at: datetime
    predictions: List[HorizonPrediction]


# ---------------------------------------------------------------------------
# Anomaly & Root Cause Schemas
# ---------------------------------------------------------------------------

class AnomalyResponse(BaseModel):
    id: Optional[int] = None
    device_id: str
    timestamp: datetime
    anomaly_score: float
    severity: str
    root_cause_code: str
    root_cause_title: str
    description: str
    recommendation: str
    sensor_contributions: Optional[Dict[str, float]] = None
    is_resolved: bool

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Alert Schemas
# ---------------------------------------------------------------------------

class AlertResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    level: str
    channel: str
    title: str
    message: str
    recommendation: Optional[str]
    acknowledged: bool

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Remediation Action Schemas (Closed-Loop Tracker FR-6.2)
# ---------------------------------------------------------------------------

class ActionCreate(BaseModel):
    device_id: str
    action_type: str  # "OPEN_WINDOW", "HEPA_PURIFIER", "EXHAUST_HOOD", "HVAC_FRESH_AIR"
    description: str


class ActionResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    action_type: str
    description: str
    initial_aqi: int
    initial_pm2_5: float
    initial_co2: float
    current_aqi: int
    target_aqi: int
    is_active: bool
    resolved_at: Optional[datetime]
    recovery_duration_mins: Optional[float]
    efficacy_score: Optional[float]

    class Config:
        from_attributes = True
