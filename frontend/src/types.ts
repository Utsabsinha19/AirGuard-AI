export interface Telemetry {
  id?: number;
  device_id: string;
  timestamp: string;
  pm0_3?: number;
  pm1_0?: number;
  pm2_5: number;
  pm10?: number;
  co2: number;
  voc: number;
  hcho?: number;
  voc_index?: number;
  nox_index?: number;
  gas_resistance?: number;
  temperature: number;
  humidity: number;
  pressure?: number;
  ambient_light?: number;
  noise_level?: number;
  battery_pct?: number;
  calibrated_pm2_5: number;
  calibrated_voc: number;
  aqi: number;
  aqi_category: string;
  aqi_color?: string;
  dominant_pollutant: string;
  diagnosis?: AnomalyDiagnosis;
  decay_constant_k?: number;
  cadr_estimate_cfm?: number;
  filter_health_status?: string;
}

export interface Device {
  id: string;
  name: string;
  room: string;
  zone?: string;
  floor: string;
  is_online: boolean;
  last_seen: string;
  firmware_version: string;
  ip_address: string;
  mac_address: string;
  x_coord?: number;
  y_coord?: number;
  latitude?: number;
  longitude?: number;
  pm_zero_offset?: number;
  pm_gain?: number;
  voc_zero_offset?: number;
  voc_gain?: number;
  latest_telemetry?: Telemetry;
}

export interface HorizonPrediction {
  horizon_mins: number;
  horizon_label: string;
  predicted_pm2_5: number;
  predicted_co2: number;
  predicted_voc: number;
  predicted_aqi: number;
  aqi_category: string;
  aqi_color: string;
  dominant_pollutant: string;
  confidence_lower: number;
  confidence_upper: number;
  model_type: string;
}

export interface PredictionData {
  device_id: string;
  current_aqi: number;
  current_category: string;
  generated_at: string;
  predictions: HorizonPrediction[];
}

export interface ModelBenchmarkItem {
  model: string;
  architecture: string;
  mae_1h: number;
  r2_1h: number;
  params: string;
  latency_ms: number;
  predictions: HorizonPrediction[];
}

export interface MultiModelComparisonData {
  device_id: string;
  current_aqi: number;
  generated_at: string;
  models: ModelBenchmarkItem[];
}

export interface AnomalyDiagnosis {
  is_anomaly: boolean;
  anomaly_score: number;
  severity: "NORMAL" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  root_cause_code: string;
  root_cause_title: string;
  description: string;
  recommendation: string;
  sensor_contributions?: {
    "PM2.5": number;
    "CO2": number;
    "VOC": number;
    "HCHO"?: number;
  };
  metrics?: {
    pm2_5: number;
    co2: number;
    voc: number;
    hcho?: number;
    temperature: number;
    humidity: number;
    pressure?: number;
    noise_level?: number;
    ambient_light?: number;
    z_pm2_5: number;
    z_co2: number;
    z_voc: number;
  };
}

export interface AlertItem {
  id: number;
  device_id: string;
  timestamp: string;
  level: "INFO" | "WARNING" | "CRITICAL";
  channel: string;
  channels?: string;
  title: string;
  message: string;
  recommendation?: string;
  acknowledged: boolean;
}

export interface RemediationAction {
  id: number;
  device_id: string;
  timestamp: string;
  action_type: string;
  description: string;
  initial_aqi: number;
  initial_pm2_5: number;
  initial_co2: number;
  current_aqi: number;
  current_pm2_5?: number;
  current_co2?: number;
  target_aqi: number;
  co2_decay_rate?: number;
  pm25_decay_rate?: number;
  recovery_message?: string;
  is_active: boolean;
  resolved_at?: string;
  recovery_duration_mins?: number;
  efficacy_score?: number;
}

// ==========================================
// v3.0 Actuation Interfaces
// ==========================================
export interface ActuatorDevice {
  actuator_id: string;
  name: string;
  protocol: "MATTER" | "HOME_ASSISTANT" | "LOCAL_RELAY" | "BACNET";
  device_type: "PURIFIER" | "DAMPER" | "WINDOW" | "FAN" | "DEHUMIDIFIER";
  room_binding: string;
  state: "OFF" | "LOW" | "MEDIUM" | "HIGH" | "AUTO";
  speed_pct: number;
  is_online: boolean;
  filter_cadr_cfm: number;
  filter_hours_used: number;
  filter_health_pct: number;
  last_actuated_at?: string;
}

export interface ActuationLog {
  id: number;
  actuator_id: string;
  timestamp: string;
  command: string;
  speed_pct: number;
  source: string;
  reason: string;
  target_aqi?: number;
  energy_wh_consumed: number;
}

// ==========================================
// v3.0 Health & Inhalation Exposure
// ==========================================
export interface UserHealthProfile {
  user_id: string;
  name: string;
  cohort: "STANDARD" | "ASTHMATIC" | "CARDIOVASCULAR" | "PEDIATRIC" | "ELDERLY";
  assigned_rooms: string[];
  max_safe_dosage_ug: number;
  current_activity: "RESTING" | "LIGHT_OFFICE" | "MODERATE_EXERCISE" | "HEAVY_ACTIVITY";
  active_alerts: boolean;
}

export interface ExposureMetrics {
  user_id: string;
  cohort: string;
  minute_ventilation_rate_m3_min: number;
  cumulative_pm2_5_dose_ug: number;
  cumulative_co2_exposure_ppm_hr: number;
  cumulative_voc_exposure_ppb_hr: number;
  cumulative_hcho_dose_ug: number;
  dosage_cap_ug: number;
  dosage_percentage_consumed: number;
  health_risk_level: "LOW" | "MODERATE" | "ELEVATED" | "HIGH" | "CRITICAL";
  clinical_recommendation: string;
}

// ==========================================
// v3.0 Spatio-Temporal Diffusion
// ==========================================
export interface RoomDiffusionNode {
  room_id: string;
  name: string;
  zone: string;
  current_aqi: number;
  current_pm2_5: number;
  current_co2: number;
  current_voc: number;
  projected_pm2_5_15m: number;
  projected_pm2_5_30m: number;
  projected_pm2_5_60m: number;
  projected_aqi_60m: number;
  risk_direction: "DIFFUSING_OUTWARD" | "RECEIVING_INFLOW" | "EQUILIBRATED";
}

export interface DiffusionEdge {
  source_room: string;
  target_room: string;
  flux_rate_pct: number;
  transport_channel: "HVAC_DUCT" | "OPEN_DOORWAY" | "HALLWAY_CORRIDOR";
}

export interface CrossRoomDiffusionResponse {
  timestamp: string;
  nodes: RoomDiffusionNode[];
  edges: DiffusionEdge[];
  summary: string;
}
