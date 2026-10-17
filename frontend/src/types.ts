export interface Telemetry {
  id?: number;
  device_id: string;
  timestamp: string;
  pm0_1?: number;
  pm0_3?: number;
  pm1_0?: number;
  pm2_5: number;
  pm10?: number;
  co2: number;
  voc: number;
  hcho?: number;
  no2_ppm?: number;
  o3_ppm?: number;
  voc_index?: number;
  nox_index?: number;
  gas_resistance?: number;
  acoustic_db?: number;
  dominant_freq_hz?: number;
  heart_rate_bpm?: number;
  hrv_ms?: number;
  spo2_pct?: number;
  respiratory_rate_bpm?: number;
  mesh_node_id?: string;
  transport_channel?: string;
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
  copilot_advisory?: string;
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

// ==========================================
// v4.0 Generative Copilot ("AirGuard Agent")
// ==========================================
export interface CopilotQueryRequest {
  query: string;
  device_id?: string;
  user_id?: string;
}

export interface CopilotResponse {
  response: string;
  incident_type?: string;
  confidence: number;
  root_cause_diagnosis?: string;
  recommended_actions: string[];
  estimated_clear_time_mins?: number;
  clinical_health_impact?: string;
  citations: string[];
}

export interface CopilotIncidentAdvisory {
  incident_code: string;
  severity: string;
  location: string;
  plain_language_advisory: string;
  suggested_action: string;
  automated_action_taken: string;
  estimated_clear_time_mins?: number;
  timestamp: string;
}

// ==========================================
// v4.0 PINN 3D Fluid Dynamics & Street Canyon
// ==========================================
export interface PINNPoint3D {
  x: number;
  y: number;
  z: number;
  velocity_u: number;
  velocity_v: number;
  velocity_w: number;
  concentration: number;
  pressure_pa: number;
  streamline_id: number;
}

export interface PINNSimulationResult {
  id: string;
  timestamp: string;
  domain_type: string;
  navier_stokes_residual: number;
  advection_flux_vector: number[];
  grid_points: PINNPoint3D[];
  vortex_intensity: number;
  predicted_clear_time_mins: number;
  optimal_purifier_coordinates: {
    x_m: number;
    y_m: number;
    z_m: number;
  };
}

export interface StreetCanyonResult {
  canyon_id: string;
  aspect_ratio: number;
  recirculation_regime: "ISOLATED_ROUGHNESS" | "WAKE_INTERFERENCE" | "SKIMMING_FLOW";
  leeward_concentration_ug_m3: number;
  windward_concentration_ug_m3: number;
  canyon_vortex_rpm: number;
  pedestrian_exposure_tier: "LOW" | "MODERATE" | "HAZARDOUS";
}

// ==========================================
// v4.0 Industrial BMS & Dynamic Grid Optimization
// ==========================================
export interface BMSDevice {
  id: string;
  name: string;
  protocol: "BACNET_IP" | "MODBUS_TCP" | "KNX" | "SPARKPLUG_B" | "MATTER";
  point_name: string;
  current_state: string;
  speed_pct: number;
  damper_pct: number;
  power_draw_kw: number;
  is_online: boolean;
}

export interface GridTariffPeriod {
  hour: number;
  tier: "OFF_PEAK" | "SHOULDER" | "PEAK" | "SOLAR_SURPLUS";
  rate_cents_per_kwh: number;
}

export interface GridOptimizationStatus {
  current_tariff_tier: string;
  current_rate_cents_per_kwh: number;
  solar_surplus_active: boolean;
  preemptive_scrubbing_engaged: boolean;
  forecasted_pm25_spike_mins: number;
  calculated_cadr_cfm: number;
  cadr_decay_constant_k?: number;
  estimated_hourly_cost_dollars: number;
  total_savings_pct: number;
}

// ==========================================
// v4.0 Swarm Mesh & Resilience
// ==========================================
export interface MeshNodeInfo {
  node_id: string;
  role: "GATEWAY" | "RELAY_NODE" | "EDGE_LEAF";
  mac_address: string;
  parent_node_id?: string;
  rssi_dbm: number;
  hop_count: number;
  active_transport: "WIFI" | "ESP_NOW_MESH" | "CELLULAR_NBIOT" | "LORAWAN";
  battery_pct: number;
  is_online: boolean;
  last_packet_at: string;
}

export interface MeshTopologyResponse {
  gateway_id: string;
  total_nodes: number;
  healthy_mesh: boolean;
  nodes: MeshNodeInfo[];
  routes: Array<{
    from: string;
    to: string;
    transport: string;
    lq_pct: number;
  }>;
  peer_consensus_status: string;
}

export interface PeerConsensusReport {
  timestamp: string;
  nodes_involved: string[];
  baseline_pm25_median: number;
  calibrated_offsets: Record<string, number>;
  drift_variance_reduction_pct: number;
}

// ==========================================
// v4.0 Wearable Biometric Fusion
// ==========================================
export interface WearableTelemetry {
  source: string;
  heart_rate_bpm: number;
  hrv_ms: number;
  spo2_pct: number;
  respiratory_rate_bpm: number;
  last_synced: string;
}

export interface DynamicIntakeResponse {
  user_id: string;
  current_heart_rate: number;
  baseline_resting_hr: number;
  dynamic_ve_lpm: number;
  cumulative_intake_pm25_ug: number;
  excess_intake_due_to_hr_pct: number;
  physiological_strain_index: "NORMAL" | "MILD_STRAIN" | "HIGH_STRAIN" | "BRONCHIAL_WARNING";
}

// ==========================================
// v4.0 Hybrid Vector Database Incident Memory
// ==========================================
export interface IncidentMemoryItem {
  incident_id: string;
  timestamp: string;
  incident_type: string;
  similarity_score: number;
  sensor_signature: Record<string, number>;
  resolution_strategy: string;
  time_to_recover_mins: number;
}

export interface IncidentMemorySearchResponse {
  query_signature: Record<string, number>;
  matched_incidents: IncidentMemoryItem[];
  suggested_playbook: string;
}

// ==========================================
// v4.0 Zero-Trust & Differential Privacy
// ==========================================
export interface CertificateVerifyResponse {
  device_id: string;
  hardware_root_of_trust: string;
  x509_cert_valid: boolean;
  tls_version: string;
  issuer: string;
  fingerprint_sha256: string;
}

export interface PrivacyAnonymizeResponse {
  dataset_id: string;
  record_count: number;
  epsilon: number;
  laplace_scale_b: number;
  anonymized_records: any[];
  differential_privacy_guaranteed: boolean;
}
