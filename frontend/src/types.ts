export interface Telemetry {
  id?: number;
  device_id: string;
  timestamp: string;
  pm2_5: number;
  pm10?: number;
  co2: number;
  voc: number;
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
}

export interface Device {
  id: string;
  name: string;
  room: string;
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
  };
  metrics?: {
    pm2_5: number;
    co2: number;
    voc: number;
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
  target_aqi: number;
  is_active: boolean;
  resolved_at?: string;
  recovery_duration_mins?: number;
  efficacy_score?: number;
}
