"""
AirGuard AI - Pydantic Request & Response Data Schemas (Enhanced)
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Telemetry Schemas
# ---------------------------------------------------------------------------

class TelemetryPayload(BaseModel):
    device_id: str = Field(..., example="AG-001")
    timestamp: Optional[datetime] = None
    pm2_5: float = Field(..., ge=0, example=12.5)
    pm10: Optional[float] = Field(None, ge=0, example=18.2)
    co2: float = Field(..., ge=300, le=10000, example=720.0)
    voc: float = Field(..., ge=0, example=145.0)
    temperature: float = Field(..., example=22.4)
    humidity: float = Field(..., ge=0, le=100, example=48.2)
    
    # Expanded Sensor Suite (Section 2.1)
    pressure: Optional[float] = Field(1013.25, example=1012.8)
    ambient_light: Optional[float] = Field(150.0, example=220.0)
    noise_level: Optional[float] = Field(42.0, example=45.0)
    battery_pct: Optional[int] = Field(95, example=88)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


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
    ambient_light: Optional[float]
    noise_level: Optional[float]
    battery_pct: Optional[int]
    calibrated_pm2_5: float
    calibrated_voc: float
    aqi: int
    aqi_category: str
    dominant_pollutant: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Device Schemas & Calibration (Section 2.2, 2.3)
# ---------------------------------------------------------------------------

class DeviceCreate(BaseModel):
    id: str = Field(..., example="AG-001")
    name: str = Field(..., example="Master Bedroom Sensor")
    room: str = Field(..., example="Bedroom")
    floor: Optional[str] = "Floor 1"
    firmware_version: Optional[str] = "v1.3.0-EXP"
    ip_address: Optional[str] = "192.168.1.101"
    mac_address: Optional[str] = "24:6F:28:AB:CD:01"
    x_coord: Optional[float] = 25.0
    y_coord: Optional[float] = 30.0


class DeviceCalibrationRequest(BaseModel):
    pm_zero_offset: Optional[float] = Field(0.0, description="PM2.5 baseline zero-point shift")
    pm_gain: Optional[float] = Field(1.0, description="PM2.5 optical gain scaling factor")
    voc_zero_offset: Optional[float] = Field(0.0, description="VOC baseline zero-point shift")
    voc_gain: Optional[float] = Field(1.0, description="VOC sensitivity gain scaling factor")


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
    x_coord: Optional[float] = 25.0
    y_coord: Optional[float] = 30.0
    latitude: Optional[float] = 37.7749
    longitude: Optional[float] = -122.4194
    pm_zero_offset: Optional[float] = 0.0
    pm_gain: Optional[float] = 1.0
    voc_zero_offset: Optional[float] = 0.0
    voc_gain: Optional[float] = 1.0
    latest_telemetry: Optional[TelemetryResponse] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Prediction & Multi-Model Comparison Schemas (Section 2.2)
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


class ModelBenchmarkItem(BaseModel):
    model: str
    architecture: str
    mae_1h: float
    r2_1h: float
    params: str
    latency_ms: float
    predictions: List[HorizonPrediction]


class MultiModelComparisonResponse(BaseModel):
    device_id: str
    current_aqi: int
    generated_at: datetime
    models: List[ModelBenchmarkItem]


# ---------------------------------------------------------------------------
# Anomaly & Alert Schemas
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
# Remediation Action Schemas (Closed-Loop Tracker)
# ---------------------------------------------------------------------------

class ActionCreate(BaseModel):
    device_id: str
    action_type: str
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
