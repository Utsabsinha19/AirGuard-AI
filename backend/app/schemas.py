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

    # Version 4.0 Speciated Matrix, Swarm Mesh & Wearable Biometric Fusion
    pm0_1: Optional[float] = Field(None, ge=0, example=0.8)             # Ultra-fine respirable particles
    no2_ppm: Optional[float] = Field(None, ge=0, example=0.02)          # Nitrogen Dioxide (SGP41/PID)
    o3_ppm: Optional[float] = Field(None, ge=0, example=0.015)          # Ground-level Ozone
    acoustic_db: Optional[float] = Field(None, ge=0, example=44.5)      # FFT sound pressure level
    dominant_freq_hz: Optional[float] = Field(None, ge=0, example=120.0)# FFT dominant acoustic frequency
    heart_rate_bpm: Optional[float] = Field(None, ge=30, le=240, example=72.0)
    hrv_ms: Optional[float] = Field(None, ge=5, le=250, example=58.0)
    spo2_pct: Optional[float] = Field(None, ge=70, le=100, example=98.5)
    respiratory_rate_bpm: Optional[float] = Field(None, ge=5, le=60, example=15.0)
    wearable_source: Optional[str] = Field("HEALTHKIT", example="HEALTHKIT")
    mesh_node_id: Optional[str] = Field(None, example="MESH-NODE-A")
    mesh_parent_id: Optional[str] = Field(None, example="GATEWAY-01")
    transport_channel: Optional[str] = Field("WIFI", example="ESP_NOW")
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
    pm0_1: Optional[float] = 0.0
    pm0_3: Optional[float] = 0.0
    pm1_0: Optional[float] = 0.0
    hcho: Optional[float] = 0.0
    no2_ppm: Optional[float] = 0.0
    o3_ppm: Optional[float] = 0.0
    voc_index: Optional[float] = 100.0
    nox_index: Optional[float] = 1.0
    gas_resistance: Optional[float] = 50000.0
    acoustic_db: Optional[float] = 40.0
    dominant_freq_hz: Optional[float] = 120.0
    heart_rate_bpm: Optional[float] = 72.0
    hrv_ms: Optional[float] = 60.0
    spo2_pct: Optional[float] = 98.0
    respiratory_rate_bpm: Optional[float] = 15.0
    wearable_source: Optional[str] = "HEALTHKIT"
    mesh_node_id: Optional[str] = None
    transport_channel: Optional[str] = "WIFI"
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


# ===========================================================================
# Version 4.0 Swarm Mesh & Multi-Transport Resilience Schemas
# ===========================================================================

class MeshNodeInfo(BaseModel):
    node_id: str
    role: str                           # "GATEWAY", "RELAY_NODE", "EDGE_LEAF"
    mac_address: str
    parent_node_id: Optional[str] = None
    rssi_dbm: int
    hop_count: int
    active_transport: str               # "WIFI", "ESP_NOW_MESH", "CELLULAR_NBIOT", "LORAWAN"
    battery_pct: int
    is_online: bool
    last_packet_at: datetime


class MeshTopologyResponse(BaseModel):
    gateway_id: str
    total_nodes: int
    healthy_mesh: bool
    nodes: List[MeshNodeInfo]
    routes: List[Dict[str, Any]]
    peer_consensus_status: str


class PeerConsensusReport(BaseModel):
    timestamp: datetime
    nodes_involved: List[str]
    baseline_pm25_median: float
    calibrated_offsets: Dict[str, float]
    drift_variance_reduction_pct: float


# ===========================================================================
# Version 4.0 Physics-Informed Neural Network (PINN 3D & Street Canyon)
# ===========================================================================

class PINNPoint3D(BaseModel):
    x: float
    y: float
    z: float
    velocity_u: float
    velocity_v: float
    velocity_w: float
    concentration: float
    pressure_pa: float
    streamline_id: int


class PINNSimulationRequest(BaseModel):
    room_or_canyon_id: str = "ROOM-LIVING-ROOM"
    inlet_velocity_mps: float = 1.2
    vent_exhaust_rate_cfm: float = 240.0
    emission_source_ug_s: float = 35.0
    resolution_x: int = 10
    resolution_y: int = 10
    resolution_z: int = 5


class PINNSimulationResponse(BaseModel):
    id: str
    timestamp: datetime
    domain_type: str                    # "INDOOR_3D_ROOM", "URBAN_STREET_CANYON"
    navier_stokes_residual: float
    advection_flux_vector: List[float]
    grid_points: List[PINNPoint3D]
    vortex_intensity: float
    predicted_clear_time_mins: float
    optimal_purifier_coordinates: Dict[str, float]


class StreetCanyonRequest(BaseModel):
    canyon_id: str = "CANYON-DOWNTOWN-01"
    building_height_m: float = 25.0
    street_width_m: float = 20.0
    ambient_wind_mps: float = 4.0
    wind_direction_deg: float = 45.0
    traffic_emissions_ug_m_s: float = 80.0


class StreetCanyonResponse(BaseModel):
    canyon_id: str
    aspect_ratio: float                 # H/W ratio
    recirculation_regime: str           # "ISOLATED_ROUGHNESS", "WAKE_INTERFERENCE", "SKIMMING_FLOW"
    leeward_concentration_ug_m3: float
    windward_concentration_ug_m3: float
    canyon_vortex_rpm: float
    pedestrian_exposure_tier: str       # "LOW", "MODERATE", "HAZARDOUS"


# ===========================================================================
# Version 4.0 Generative Environmental Health Copilot ("AirGuard Agent")
# ===========================================================================

class CopilotQueryRequest(BaseModel):
    query: str
    device_id: Optional[str] = "AG-001"
    user_id: Optional[str] = "default_user"
    include_raw_telemetry: Optional[bool] = True


class CopilotResponse(BaseModel):
    response: str
    incident_type: Optional[str] = None
    confidence: float
    root_cause_diagnosis: Optional[str] = None
    recommended_actions: List[str]
    estimated_clear_time_mins: Optional[float] = None
    clinical_health_impact: Optional[str] = None
    citations: List[str]


class CopilotIncidentAdvisory(BaseModel):
    incident_code: str
    severity: str
    location: str
    plain_language_advisory: str
    suggested_action: str
    automated_action_taken: str
    timestamp: datetime


# ===========================================================================
# Version 4.0 Industrial BMS & Dynamic Grid Demand Response
# ===========================================================================

class BMSDeviceControlRequest(BaseModel):
    device_id: str
    target_speed_pct: Optional[int] = None
    damper_pct: Optional[int] = None
    chiller_temp_c: Optional[float] = None
    operating_mode: Optional[str] = "AUTO"


class BMSDeviceResponse(BaseModel):
    id: str
    name: str
    protocol: str                       # "BACNET_IP", "MODBUS_TCP", "KNX", "SPARKPLUG_B", "MATTER"
    point_name: str
    current_state: str
    speed_pct: int
    damper_pct: int
    power_draw_kw: float
    is_online: bool


class GridTariffPeriod(BaseModel):
    hour: int
    tier: str                           # "OFF_PEAK", "SHOULDER", "PEAK", "SOLAR_SURPLUS"
    tariff_rate_cents_per_kwh: float


class GridOptimizationStatus(BaseModel):
    current_tariff_tier: str
    current_rate_cents_per_kwh: float
    solar_surplus_active: bool
    preemptive_scrubbing_engaged: bool
    forecasted_pm25_spike_mins: int
    calculated_cadr_cfm: float
    estimated_hourly_cost_dollars: float
    total_savings_pct: float


class PreemptiveScrubSchedule(BaseModel):
    actuator_id: str
    scheduled_start: datetime
    duration_mins: int
    target_fan_speed: str
    tariff_tier_utilized: str
    projected_ug_removed: float
    projected_energy_cost_cents: float


# ===========================================================================
# Version 4.0 Hybrid Storage & Incident Vector Database Memory
# ===========================================================================

class IncidentMemoryItem(BaseModel):
    incident_id: str
    timestamp: datetime
    incident_type: str
    similarity_score: float             # Cosine similarity 0.0 - 1.0
    sensor_signature: Dict[str, float]
    resolution_strategy: str
    time_to_recover_mins: float


class IncidentMemorySearchRequest(BaseModel):
    pm2_5: float
    co2: float
    voc: float
    hcho: Optional[float] = 0.0
    acoustic_db: Optional[float] = 40.0
    top_k: Optional[int] = 5


class IncidentMemorySearchResponse(BaseModel):
    query_signature: Dict[str, float]
    matched_incidents: List[IncidentMemoryItem]
    suggested_playbook: str


# ===========================================================================
# Version 4.0 Zero-Trust Security & Differential Privacy
# ===========================================================================

class PrivacyAnonymizeRequest(BaseModel):
    dataset_id: str = "MUNICIPAL-HEALTH-COHORT"
    epsilon: Optional[float] = 0.5
    delta: Optional[float] = 1e-5
    records: List[Dict[str, Any]]


class PrivacyAnonymizeResponse(BaseModel):
    dataset_id: str
    record_count: int
    epsilon: float
    laplace_scale_b: float
    anonymized_records: List[Dict[str, Any]]
    differential_privacy_guaranteed: bool


class CertificateVerifyResponse(BaseModel):
    device_id: str
    hardware_root_of_trust: str         # "ATECC608A_SECURE_ELEMENT"
    x509_cert_valid: bool
    tls_version: str
    issuer: str
    fingerprint_sha256: str


# ===========================================================================
# Version 4.0 Wearable Biometric Telemetry & Inhalation Dosage
# ===========================================================================

class WearableSyncRequest(BaseModel):
    user_id: str = "default_user"
    source: str = "APPLE_HEALTHKIT"     # "APPLE_HEALTHKIT", "GOOGLE_HEALTH_CONNECT", "GARMIN", "WHOOP"
    heart_rate_bpm: float
    hrv_ms: float
    spo2_pct: float
    respiratory_rate_bpm: float


class DynamicIntakeResponse(BaseModel):
    user_id: str
    current_heart_rate: float
    baseline_resting_hr: float
    dynamic_ve_lpm: float
    cumulative_intake_pm25_ug: float
    excess_intake_due_to_hr_pct: float
    physiological_strain_index: str     # "NORMAL", "MILD_STRAIN", "HIGH_STRAIN", "BRONCHIAL_WARNING"
