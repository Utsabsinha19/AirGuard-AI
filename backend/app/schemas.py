"""
AirGuard AI - Pydantic Request & Response Data Schemas (Enhanced)
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Telemetry Schemas (v1.0 & v2.0 Nested Schemas)
# ---------------------------------------------------------------------------

class TelemetryPayload(BaseModel):
    device_id: str = Field(..., example="AG-001")
    location: Optional[str] = None
    timestamp: Optional[datetime] = None
    pm2_5: Optional[float] = Field(None, ge=0, example=12.5)
    pm10: Optional[float] = Field(None, ge=0, example=18.2)
    co2: Optional[float] = Field(None, ge=300, le=10000, example=720.0)
    voc: Optional[float] = Field(None, ge=0, example=145.0)
    temperature: Optional[float] = Field(None, example=22.4)
    humidity: Optional[float] = Field(None, ge=0, le=100, example=48.2)
    
    # Expanded Sensor Suite (Section 2.1 & v3.0)
    pressure: Optional[float] = Field(1013.25, example=1012.8)
    ambient_light: Optional[float] = Field(150.0, example=220.0)
    noise_level: Optional[float] = Field(42.0, example=45.0)
    battery_pct: Optional[int] = Field(95, example=88)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Next-Gen Sensor Matrix (v3.0 Section 1.1)
    pm0_3: Optional[float] = Field(None, ge=0, example=2.1)
    pm1_0: Optional[float] = Field(None, ge=0, example=5.4)
    hcho: Optional[float] = Field(None, ge=0, example=0.03)            # Formaldehyde in ppm
    voc_index: Optional[float] = Field(None, ge=0, example=115.0)      # Sensirion VOC Index
    nox_index: Optional[float] = Field(None, ge=0, example=1.2)        # Sensirion NOx Index
    gas_resistance: Optional[float] = Field(None, ge=0, example=52000.0) # BME688 in Ohms
    metrics: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def extract_metrics(cls, data: Any) -> Any:
        if isinstance(data, dict):
            metrics = data.get("metrics")
            if isinstance(metrics, dict):
                for k, v in metrics.items():
                    if k not in data or data[k] is None:
                        data[k] = v
            # default fallback if primary fields were omitted
            if data.get("pm2_5") is None:
                data["pm2_5"] = 10.0
            if data.get("co2") is None:
                data["co2"] = 600.0
            if data.get("voc") is None:
                data["voc"] = 100.0
            if data.get("temperature") is None:
                data["temperature"] = 22.0
            if data.get("humidity") is None:
                data["humidity"] = 45.0
        return data


class TelemetryResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    pm2_5: float
    pm10: Optional[float] = None
    pm0_3: Optional[float] = 0.0
    pm1_0: Optional[float] = 0.0
    hcho: Optional[float] = 0.0
    voc_index: Optional[float] = 100.0
    nox_index: Optional[float] = 1.0
    gas_resistance: Optional[float] = 50000.0
    co2: float
    voc: float
    temperature: float
    humidity: float
    pressure: Optional[float] = None
    ambient_light: Optional[float] = None
    noise_level: Optional[float] = None
    battery_pct: Optional[int] = None
    calibrated_pm2_5: float
    calibrated_voc: float
    aqi: int
    aqi_category: str
    dominant_pollutant: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Device Schemas & Calibration (Section 2.2, 2.3, 4.1)
# ---------------------------------------------------------------------------

class DeviceCreate(BaseModel):
    id: str = Field(..., example="AG-001")
    name: str = Field(..., example="Master Bedroom Sensor")
    room: str = Field(..., example="Bedroom")
    zone: Optional[str] = Field("Bedroom", example="Bedroom")
    floor: Optional[str] = "Floor 1"
    firmware_version: Optional[str] = "v2.0.0-PRO"
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
    zone: Optional[str] = "Indoor"
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
# Anomaly & Alert Schemas (Section 3.3 Multi-Channel)
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
    channels: Optional[str] = "WEB_DASHBOARD_TOAST,APP_PUSH"
    title: str
    message: str
    recommendation: Optional[str]
    acknowledged: bool

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Remediation Action Schemas (Closed-Loop Tracker, Section 4.2)
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
    current_pm2_5: Optional[float] = None
    current_co2: Optional[float] = None
    target_aqi: int
    co2_decay_rate: Optional[float] = None
    pm25_decay_rate: Optional[float] = None
    decay_constant_k: Optional[float] = None
    cadr_estimate_cfm: Optional[float] = None
    filter_health_status: Optional[str] = "NOMINAL"
    recovery_message: Optional[str] = None
    is_active: bool
    resolved_at: Optional[datetime] = None
    recovery_duration_mins: Optional[float] = None
    efficacy_score: Optional[float] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Version 3.0 Smart Home Actuation Schemas (Matter / Home Assistant)
# ---------------------------------------------------------------------------

class ActuatorControlRequest(BaseModel):
    actuator_id: str
    state: Optional[str] = None          # "ON", "OFF", "AUTO", "OPEN", "CLOSED"
    fan_speed: Optional[str] = None      # "OFF", "LOW", "MED", "HIGH", "BOOST", "AUTO"
    damper_position: Optional[int] = None # 0 - 100%
    window_open_pct: Optional[int] = None # 0 - 100%
    auto_mode: Optional[bool] = None


class ActuatorResponse(BaseModel):
    id: str
    name: str
    room: str
    device_type: str
    protocol: str
    is_online: bool
    state: str
    fan_speed: str
    damper_position: int
    window_open_pct: int
    auto_mode: bool
    last_actuated_at: datetime

    class Config:
        from_attributes = True


class ActuationLogResponse(BaseModel):
    id: int
    actuator_id: str
    timestamp: datetime
    trigger_type: str
    action_taken: str
    reason: str
    status: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Version 3.0 Personal Health Exposure Schemas (Section 5.1 & 5.2)
# ---------------------------------------------------------------------------

class HealthProfileUpdateRequest(BaseModel):
    user_id: Optional[str] = "default_user"
    profile_type: str                   # "STANDARD", "ASTHMATIC", "CARDIOVASCULAR", "PEDIATRIC", "ELDERLY"
    minute_ventilation_rate: Optional[float] = None
    target_pm25_limit: Optional[float] = None
    target_co2_limit: Optional[float] = None
    target_hcho_limit: Optional[float] = None


class HealthProfileResponse(BaseModel):
    id: int
    user_id: str
    profile_type: str
    minute_ventilation_rate: float
    target_pm25_limit: float
    target_co2_limit: float
    target_hcho_limit: float
    updated_at: datetime

    class Config:
        from_attributes = True


class ExposureMetricsResponse(BaseModel):
    user_id: str
    profile_type: str
    time_window_hours: float
    minute_ventilation_rate_lpm: float
    cumulative_intake_pm25_ug: float
    cumulative_intake_co2_mg: float
    cumulative_intake_voc_ug: float
    cumulative_intake_hcho_ug: float
    health_risk_score: float             # 0 to 100
    clinical_risk_tier: str             # "LOW", "MODERATE", "ELEVATED", "HIGH_HAZARD"
    who_guideline_exceeded: bool
    personalized_precautions: List[str]


# ---------------------------------------------------------------------------
# Version 3.0 Cross-Room Diffusion Schemas (ST-GNN, Section 2.1)
# ---------------------------------------------------------------------------

class RoomDiffusionNode(BaseModel):
    room_id: str
    room_name: str
    current_pm2_5: float
    predicted_pm2_5_15m: float
    predicted_pm2_5_30m: float
    predicted_pm2_5_60m: float
    diffusion_risk: str                 # "LOW", "MODERATE", "HIGH"


class DiffusionEdge(BaseModel):
    source_room: str
    target_room: str
    diffusion_weight: float             # Spatial coupling coefficient
    airflow_direction: str


class CrossRoomDiffusionResponse(BaseModel):
    timestamp: datetime
    active_source: Optional[str]
    nodes: List[RoomDiffusionNode]
    edges: List[DiffusionEdge]
    highest_dispersion_path: str
    mitigation_advice: str
