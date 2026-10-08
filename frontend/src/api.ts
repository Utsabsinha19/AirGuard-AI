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

export async function fetchExposureMetrics(userId = "user_default"): Promise<ExposureMetrics> {
  const res = await fetch(`${API_BASE}/health/exposure/${userId}`);
  if (!res.ok) throw new Error("Failed to fetch exposure metrics");
  return res.json();
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
