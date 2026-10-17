import type {
  Device,
  Telemetry,
  PredictionData,
  MultiModelComparisonData,
  AnomalyDiagnosis,
  AlertItem,
  RemediationAction,
  ActuatorDevice,
  ActuationLog,
  UserHealthProfile,
  ExposureMetrics,
  CrossRoomDiffusionResponse,
  CopilotResponse,
  CopilotIncidentAdvisory,
  PINNSimulationResult,
  StreetCanyonResult,
  BMSDevice,
  GridOptimizationStatus,
  MeshTopologyResponse,
  PeerConsensusReport,
  DynamicIntakeResponse,
  IncidentMemorySearchResponse,
  CertificateVerifyResponse,
  PrivacyAnonymizeResponse,
} from "./types";

const API_BASE = "http://127.0.0.1:8000/api";

export async function fetchDevices(): Promise<Device[]> {
  const res = await fetch(`${API_BASE}/devices`);
  if (!res.ok) throw new Error("Failed to fetch devices");
  return res.json();
}

export async function fetchLatestTelemetry(deviceId: string): Promise<Telemetry> {
  const res = await fetch(`${API_BASE}/telemetry/latest/${deviceId}`);
  if (!res.ok) throw new Error("Failed to fetch latest telemetry");
  return res.json();
}

export async function fetchHistory(deviceId: string, limit = 60): Promise<Telemetry[]> {
  const res = await fetch(`${API_BASE}/telemetry/history/${deviceId}?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch history");
  return res.json();
}

export async function fetchPredictions(
  deviceId: string,
  modelType: string = "baseline"
): Promise<PredictionData> {
  const res = await fetch(`${API_BASE}/predictions/${deviceId}?model_type=${modelType}`);
  if (!res.ok) throw new Error("Failed to fetch predictions");
  return res.json();
}

export async function fetchModelComparison(deviceId: string): Promise<MultiModelComparisonData> {
  const res = await fetch(`${API_BASE}/predictions/compare/${deviceId}`);
  if (!res.ok) throw new Error("Failed to fetch multi-model comparison");
  return res.json();
}

export async function calibrateDevice(
  deviceId: string,
  params: { pm_zero_offset?: number; pm_gain?: number; voc_zero_offset?: number; voc_gain?: number }
): Promise<Device> {
  const res = await fetch(`${API_BASE}/devices/${deviceId}/calibrate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error("Failed to calibrate device");
  return res.json();
}

export async function fetchLiveDiagnosis(deviceId: string): Promise<AnomalyDiagnosis> {
  const res = await fetch(`${API_BASE}/anomalies/diagnose/${deviceId}`);
  if (!res.ok) throw new Error("Failed to fetch anomaly diagnosis");
  return res.json();
}

export async function fetchAlerts(unacknowledgedOnly = false): Promise<AlertItem[]> {
  const res = await fetch(`${API_BASE}/alerts?unacknowledged_only=${unacknowledgedOnly}`);
  if (!res.ok) throw new Error("Failed to fetch alerts");
  return res.json();
}

export async function acknowledgeAlert(alertId: number): Promise<AlertItem> {
  const res = await fetch(`${API_BASE}/alerts/${alertId}/ack`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to acknowledge alert");
  return res.json();
}

export async function acknowledgeAllAlerts(): Promise<void> {
  const res = await fetch(`${API_BASE}/alerts/ack-all`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to acknowledge all alerts");
}

export async function convertAlertToAction(alertId: number): Promise<RemediationAction> {
  const res = await fetch(`${API_BASE}/alerts/${alertId}/convert-to-action`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to convert alert to action");
  return res.json();
}

export async function fetchActiveAction(deviceId: string): Promise<RemediationAction | null> {
  const res = await fetch(`${API_BASE}/actions/active/${deviceId}`);
  if (!res.ok) return null;
  return res.json();
}

export async function logRemediationAction(
  deviceId: string,
  actionType: string,
  description: string
): Promise<RemediationAction> {
  const res = await fetch(`${API_BASE}/actions/log`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      device_id: deviceId,
      action_type: actionType,
      description,
    }),
  });
  if (!res.ok) throw new Error("Failed to log remediation action");
  return res.json();
}

export async function resolveRemediationAction(actionId: number): Promise<RemediationAction> {
  const res = await fetch(`${API_BASE}/actions/${actionId}/resolve`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to resolve action");
  return res.json();
}

export async function triggerSimulatorScenario(
  scenario: string,
  deviceId: string
): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/simulator/trigger`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario, device_id: deviceId }),
  });
  if (!res.ok) throw new Error("Failed to trigger simulation scenario");
  return res.json();
}

export function getExportCSVUrl(deviceId: string): string {
  return `${API_BASE}/telemetry/export/${deviceId}`;
}

// ==========================================
// v3.0 Actuation & Matter API
// ==========================================

export async function fetchActuators(): Promise<ActuatorDevice[]> {
  const res = await fetch(`${API_BASE}/actuation/devices`);
  if (!res.ok) throw new Error("Failed to fetch actuators");
  return res.json();
}

export async function controlActuator(
  actuatorId: string,
  command: string,
  speedPct = 100,
  source = "DASHBOARD_UI",
  reason = "User manual trigger"
): Promise<ActuatorDevice> {
  const res = await fetch(`${API_BASE}/actuation/control`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      actuator_id: actuatorId,
      command,
      speed_pct: speedPct,
      source,
      reason,
    }),
  });
  if (!res.ok) throw new Error("Failed to control actuator");
  return res.json();
}

export async function fetchActuationLogs(actuatorId?: string, limit = 50): Promise<ActuationLog[]> {
  const query = actuatorId ? `?actuator_id=${actuatorId}&limit=${limit}` : `?limit=${limit}`;
  const res = await fetch(`${API_BASE}/actuation/logs${query}`);
  if (!res.ok) throw new Error("Failed to fetch actuation logs");
  return res.json();
}

export async function evaluateActuation(deviceId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/actuation/evaluate/${deviceId}`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to evaluate actuation");
  return res.json();
}

// ==========================================
// v3.0 Health Exposure & Risk API
// ==========================================
export async function fetchUserProfiles(): Promise<UserHealthProfile[]> {
  const res = await fetch(`${API_BASE}/health/profiles`);
  if (!res.ok) throw new Error("Failed to fetch user profiles");
  return res.json();
}

export async function fetchExposureMetrics(userId = "default_user"): Promise<ExposureMetrics> {
  const res = await fetch(`${API_BASE}/health/exposure?user_id=${userId}`);
  if (!res.ok) throw new Error("Failed to fetch exposure metrics");
  const raw = await res.json();
  const cap = raw.dosage_cap_ug ?? 50.0;
  const pmDose = raw.cumulative_intake_pm25_ug ?? raw.cumulative_pm2_5_dose_ug ?? 12.4;
  const pct = raw.dosage_percentage_consumed ?? Math.min(100, (pmDose / cap) * 100);
  return {
    user_id: raw.user_id,
    cohort: raw.profile_type ?? raw.cohort ?? "STANDARD",
    minute_ventilation_rate_m3_min: (raw.minute_ventilation_rate_lpm ? raw.minute_ventilation_rate_lpm / 1000 : raw.minute_ventilation_rate_m3_min) ?? 0.012,
    cumulative_pm2_5_dose_ug: pmDose,
    cumulative_co2_exposure_ppm_hr: raw.cumulative_intake_co2_mg ? raw.cumulative_intake_co2_mg / 1.8 : (raw.cumulative_co2_exposure_ppm_hr ?? 620),
    cumulative_voc_exposure_ppb_hr: raw.cumulative_intake_voc_ug ?? raw.cumulative_voc_exposure_ppb_hr ?? 120,
    cumulative_hcho_dose_ug: raw.cumulative_intake_hcho_ug ?? raw.cumulative_hcho_dose_ug ?? 0.32,
    dosage_cap_ug: cap,
    dosage_percentage_consumed: pct,
    health_risk_level: (raw.clinical_risk_tier ?? raw.health_risk_level ?? "LOW") as any,
    clinical_recommendation: (Array.isArray(raw.personalized_precautions) ? raw.personalized_precautions.join(" ") : raw.personalized_precautions) ?? raw.clinical_recommendation ?? "Current inhalation dosage is within healthy clinical guidelines.",
  };
}

export async function updateHealthProfile(
  profile: Partial<UserHealthProfile> & { user_id: string }
): Promise<UserHealthProfile> {
  const res = await fetch(`${API_BASE}/health/profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });
  if (!res.ok) throw new Error("Failed to update health profile");
  return res.json();
}

// ==========================================
// v3.0 Spatio-Temporal Diffusion & Federated Sync
// ==========================================
export async function fetchCrossRoomDiffusion(): Promise<CrossRoomDiffusionResponse> {
  const res = await fetch(`${API_BASE}/predictions/diffusion/cross-room`);
  if (!res.ok) throw new Error("Failed to fetch cross room diffusion");
  return res.json();
}

export async function federatedCalibrateDevice(
  deviceId: string
): Promise<{ status: string; zero_point_reference_pm2_5: number; sync_timestamp: string }> {
  const res = await fetch(`${API_BASE}/devices/${deviceId}/federated-calibrate`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to perform federated calibration");
  return res.json();
}

// ==========================================
// Version 4.0 API Client Functions
// ==========================================

export async function queryCopilotAgent(
  query: string,
  deviceId = "AG-001",
  userId = "default_user"
): Promise<CopilotResponse> {
  const res = await fetch(`${API_BASE}/copilot/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, device_id: deviceId, user_id: userId }),
  });
  if (!res.ok) throw new Error("Failed to query Copilot Agent");
  return res.json();
}

export async function fetchCopilotAdvisory(
  deviceId: string,
  incidentCode = "CLEAN_STABLE",
  room = "Living Room"
): Promise<CopilotIncidentAdvisory> {
  const res = await fetch(
    `${API_BASE}/copilot/advisories/${deviceId}?incident_code=${incidentCode}&room=${encodeURIComponent(room)}`
  );
  if (!res.ok) throw new Error("Failed to fetch Copilot Advisory");
  return res.json();
}

export async function runPINN3DSimulation(params?: {
  room_or_canyon_id?: string;
  inlet_velocity_mps?: number;
  vent_exhaust_rate_cfm?: number;
  emission_source_ug_s?: number;
  resolution_x?: number;
  resolution_y?: number;
  resolution_z?: number;
}): Promise<PINNSimulationResult> {
  const res = await fetch(`${API_BASE}/pinn/simulate-3d`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params || {}),
  });
  if (!res.ok) throw new Error("Failed to run PINN 3D simulation");
  return res.json();
}

export async function runPINNStreetCanyon(params?: {
  canyon_id?: string;
  building_height_m?: number;
  street_width_m?: number;
  ambient_wind_mps?: number;
  wind_direction_deg?: number;
  traffic_emissions_ug_m_s?: number;
}): Promise<StreetCanyonResult> {
  const res = await fetch(`${API_BASE}/pinn/street-canyon`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params || {}),
  });
  if (!res.ok) throw new Error("Failed to run PINN Street Canyon simulation");
  return res.json();
}

export async function fetchBMSDevices(): Promise<BMSDevice[]> {
  const res = await fetch(`${API_BASE}/bms/devices`);
  if (!res.ok) throw new Error("Failed to fetch BMS devices");
  return res.json();
}

export async function controlBMSDevice(
  deviceId: string,
  targetSpeedPct?: number,
  damperPct?: number,
  mode = "AUTO"
): Promise<BMSDevice> {
  const res = await fetch(`${API_BASE}/bms/control`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      device_id: deviceId,
      target_speed_pct: targetSpeedPct,
      damper_pct: damperPct,
      operating_mode: mode,
    }),
  });
  if (!res.ok) throw new Error("Failed to control BMS device");
  return res.json();
}

export async function fetchGridTariffs(): Promise<{
  current_tariff: { hour: number; tier: string; rate_cents_per_kwh: number; is_solar_surplus: boolean };
  tariffs_24h: Record<number, { tier: string; rate: number }>;
}> {
  const res = await fetch(`${API_BASE}/grid/tariffs`);
  if (!res.ok) throw new Error("Failed to fetch grid tariffs");
  return res.json();
}

export async function evaluateGridDemandResponse(
  spikeMins = 20,
  forecastedPm25 = 65.0
): Promise<GridOptimizationStatus> {
  const res = await fetch(
    `${API_BASE}/grid/evaluate-response?predicted_pm25_spike_mins=${spikeMins}&forecasted_pm25=${forecastedPm25}`,
    { method: "POST" }
  );
  if (!res.ok) throw new Error("Failed to evaluate grid demand response");
  return res.json();
}

export async function fetchMeshTopology(): Promise<MeshTopologyResponse> {
  const res = await fetch(`${API_BASE}/mesh/topology`);
  if (!res.ok) throw new Error("Failed to fetch mesh topology");
  return res.json();
}

export async function triggerPeerConsensus(): Promise<PeerConsensusReport> {
  const res = await fetch(`${API_BASE}/mesh/peer-consensus`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger peer consensus");
  return res.json();
}

export async function syncWearable(payload: {
  user_id: string;
  source: string;
  heart_rate_bpm: number;
  hrv_ms: number;
  spo2_pct: number;
  respiratory_rate_bpm: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/wearables/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to sync wearable");
  return res.json();
}

export async function fetchDynamicInhalationIntake(userId = "default_user"): Promise<DynamicIntakeResponse> {
  const res = await fetch(`${API_BASE}/wearables/${userId}/dynamic-intake`);
  if (!res.ok) throw new Error("Failed to fetch dynamic inhalation intake");
  return res.json();
}

export async function searchIncidentVectorMemory(sig: {
  pm2_5: number;
  co2: number;
  voc: number;
  hcho?: number;
  acoustic_db?: number;
  top_k?: number;
}): Promise<IncidentMemorySearchResponse> {
  const res = await fetch(`${API_BASE}/vector-memory/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(sig),
  });
  if (!res.ok) throw new Error("Failed to search vector memory");
  return res.json();
}

export async function verifyDeviceHardwareCert(deviceId: string): Promise<CertificateVerifyResponse> {
  const res = await fetch(`${API_BASE}/security/device-cert/${deviceId}`);
  if (!res.ok) throw new Error("Failed to verify device cert");
  return res.json();
}

export async function applyDifferentialPrivacy(
  datasetId: string,
  records: any[],
  epsilon = 0.5
): Promise<PrivacyAnonymizeResponse> {
  const res = await fetch(`${API_BASE}/security/differential-privacy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, records, epsilon }),
  });
  if (!res.ok) throw new Error("Failed to apply differential privacy");
  return res.json();
}
